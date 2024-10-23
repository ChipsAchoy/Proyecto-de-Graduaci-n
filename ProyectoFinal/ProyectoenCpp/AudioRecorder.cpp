#include <iostream>
#include <portaudio.h>
#include <vector>
#include <thread>
#include <atomic>
#include <cstdio>
#include "AudioFileWriter.cpp"
#include "AudioEffectProcessor.cpp"

#define SAMPLE_RATE 44100
#define FRAMES_PER_BUFFER 512
#define NUM_CHANNELS 1

typedef float SAMPLE;

class AudioRecorder
{
public:
    AudioRecorder() : recording(false), stream(nullptr) {}

    ~AudioRecorder()
    {
        if (stream)
        {
            Pa_CloseStream(stream);
        }
        Pa_Terminate();
    }

    bool initialize()
    {
        PaError err = Pa_Initialize();
        if (err != paNoError)
        {
            std::cerr << "Error al inicializar PortAudio: " << Pa_GetErrorText(err) << std::endl;
            return false;
        }

        err = Pa_OpenDefaultStream(&stream, NUM_CHANNELS, 0, paFloat32, SAMPLE_RATE, FRAMES_PER_BUFFER, &AudioRecorder::recordCallback, this);
        if (err != paNoError)
        {
            std::cerr << "Error al abrir stream: " << Pa_GetErrorText(err) << std::endl;
            return false;
        }

        return true;
    }

    void startRecording(std::string fileNameIn, std::string formatIn, std::string effectApp)
    {
        this->fileName = fileNameIn;
        this->format = formatIn;
        this->effect = effectApp;

        if (!stream)
            return;

        recording = true;
        PaError err = Pa_StartStream(stream);
        if (err != paNoError)
        {
            std::cerr << "Error al iniciar stream: " << Pa_GetErrorText(err) << std::endl;
            return;
        }
        
    }

    void stopRecording()
    {
        recording = false;

        PaError err = Pa_StopStream(stream);
        if (err != paNoError)
        {
            std::cerr << "Error al detener stream: " << Pa_GetErrorText(err) << std::endl;
            return;
        }

        saveRecording();
    }
    std::vector<SAMPLE> getBuffer()
    {	
    	std::vector<SAMPLE> bufferSend = buffer;
   // 	
        return bufferSend; // Return a copy of the buffer
        
    }
    
    void clearBuffer(){
    
    	buffer.clear();
    }

private:
    std::vector<SAMPLE> buffer;
    std::atomic<bool> recording;
    std::string fileName;
    std::string format;
    std::string effect;
    PaStream *stream;
    std::thread inputThread;

    static int recordCallback(const void *inputBuffer, void *, unsigned long framesPerBuffer,
                              const PaStreamCallbackTimeInfo *, PaStreamCallbackFlags,
                              void *userData)
    {
        AudioRecorder *recorder = static_cast<AudioRecorder *>(userData);
        const SAMPLE *in = static_cast<const SAMPLE *>(inputBuffer);

        if (inputBuffer != nullptr && recorder->recording)
        {
            if (NUM_CHANNELS == 2) // Si estamos grabando en estéreo
            {
                for (unsigned int i = 0; i < framesPerBuffer * NUM_CHANNELS; ++i)
                {
                    recorder->buffer.push_back(in[i]);
                }
            }
            else if (NUM_CHANNELS == 1) // Si estamos grabando en mono
            {
                for (unsigned int i = 0; i < framesPerBuffer; ++i)
                {
                    recorder->buffer.push_back(in[i]);
                }
            }
        }

        return recorder->recording ? paContinue : paComplete;
    }

    void saveRecording()
    {

        if (this->effect != "")
        {
            AudioEffectProcessor processor;
            processor.applyEffect(effect, this->buffer, SAMPLE_RATE);
        }

        AudioFileWriter writer;
        if (this->format == "wav")
        {
            writer.saveAsWAV(this->fileName + ".wav", this->buffer, SAMPLE_RATE, NUM_CHANNELS);
        }
        else if (this->format == "mp3")
        {
            writer.saveAsMP3(this->fileName + ".mp3", this->buffer, SAMPLE_RATE, NUM_CHANNELS);
        }
        else
        {
            std::cerr << "Formato no soportado: " << format << std::endl;
        }
    }
};
