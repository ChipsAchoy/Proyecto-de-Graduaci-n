#include <iostream>
#include <vector>
#include <sndfile.h>
#include <lame/lame.h>

typedef float SAMPLE;

class AudioFileWriter
{
public:
    bool saveAsWAV(const std::string &filename, const std::vector<SAMPLE> &buffer, int sampleRate, int numChannels)
    {
        try
        {
            SF_INFO sfinfo;
            sfinfo.channels = numChannels;
            sfinfo.samplerate = sampleRate;
            sfinfo.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;

            SNDFILE *file = sf_open(filename.c_str(), SFM_WRITE, &sfinfo);
            if (!file)
            {
                std::cerr << "Error al abrir archivo WAV: " << sf_strerror(file) << std::endl;
                return false;
            }

            // Escribir los datos en el archivo WAV
            sf_count_t numFrames = buffer.size() / numChannels;
            sf_writef_float(file, buffer.data(), numFrames);

            sf_close(file);
            std::cout << "Archivo guardado como WAV: " << filename << std::endl;
        }
        catch (const std::exception &e)
        {
            // Manejo de la excepción
            std::cerr << "Excepción capturada: " << e.what() << std::endl;
        }
        return true;
    }

    bool saveAsMP3(const std::string &filename, const std::vector<SAMPLE> &buffer, int sampleRate, int numChannels)
    {
        FILE *mp3File = fopen(filename.c_str(), "wb");
        if (!mp3File)
        {
            std::cerr << "Error al abrir archivo MP3." << std::endl;
            return false;
        }

        lame_t lame = lame_init();
        lame_set_in_samplerate(lame, sampleRate);
        lame_set_num_channels(lame, numChannels);
        lame_set_quality(lame, 5); // 2 = alta calidad, 5 = media

        if (lame_init_params(lame) < 0)
        {
            std::cerr << "Error al inicializar LAME." << std::endl;
            fclose(mp3File);
            lame_close(lame);
            return false;
        }

        const int bufferSize = 7200 + (1.25 * buffer.size());
        std::vector<unsigned char> mp3Buffer(bufferSize);

        int numSamples = buffer.size();
        int numBytes = 0;

        // Si es mono, usamos la función para buffer mono
        if (numChannels == 1)
        {
            numBytes = lame_encode_buffer_ieee_float(lame, (float *)buffer.data(), nullptr, numSamples, mp3Buffer.data(), mp3Buffer.size());
        }
        // Si es estéreo, usamos la función para datos intercalados
        else if (numChannels == 2)
        {
            numBytes = lame_encode_buffer_interleaved_ieee_float(lame, (float *)buffer.data(), numSamples / numChannels, mp3Buffer.data(), mp3Buffer.size());
        }

        if (numBytes < 0)
        {
            std::cerr << "Error al codificar MP3." << std::endl;
            fclose(mp3File);
            lame_close(lame);
            return false;
        }

        fwrite(mp3Buffer.data(), 1, numBytes, mp3File);

        // Finalizar el archivo MP3
        numBytes = lame_encode_flush(lame, mp3Buffer.data(), mp3Buffer.size());
        fwrite(mp3Buffer.data(), 1, numBytes, mp3File);

        fclose(mp3File);
        lame_close(lame);
        std::cout << "Archivo guardado como MP3: " << filename << std::endl;
        return true;
    }
};
