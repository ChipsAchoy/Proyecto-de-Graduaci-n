
#include <lame/lame.h>
#include <vector>
#include <cmath>
#include <iostream>

typedef float SAMPLE;

class AudioEffectProcessor
{
public:
    // Función para aplicar efectos
    void applyEffect(const std::string &effectType, std::vector<SAMPLE> &buffer, int sampleRate)
    {
        if (effectType == "delay")
        {
            applyDelay(buffer, sampleRate, 0.5f, 0.5f); // Delay de 500ms con feedback 50%
        }
        else if (effectType == "reverb")
        {
            applyReverb(buffer, sampleRate, 0.5f); // Reverb con decaimiento de 30%
        }
        else if (effectType == "distortion")
        {
            applyDistortion(buffer, 5.0f, 0.8f); // Ganancia de 5x y threshold de 0.8
        }
        else if (effectType == "chorus")
        {
            applyChorus(buffer, sampleRate, 0.02f, 2.0f); // Chorus con profundidad 0.02s y rate 1Hz
        }
        else
        {
            std::cerr << "Efecto no soportado: " << effectType << std::endl;
        }
    }

private:
    // Funciones de efectos
    void applyDelay(std::vector<SAMPLE> &buffer, int sampleRate, float delayTimeInSeconds, float feedback)
    {
        int delaySamples = static_cast<int>(delayTimeInSeconds * sampleRate);
        std::vector<SAMPLE> delayedBuffer(buffer.size(), 0);

        for (size_t i = 0; i < buffer.size(); ++i)
        {
            delayedBuffer[i] = buffer[i];
            if (i >= static_cast<size_t>(delaySamples))
            { // Verificación de índices
                buffer[i] += delayedBuffer[i - delaySamples] * feedback;
            }
        }
    }

    void applyReverb(std::vector<SAMPLE> &buffer, int sampleRate, float reverbDecay)
    {
        const int combFilterDelay = sampleRate / 20; // Aproximadamente 50ms delay
        for (size_t i = combFilterDelay; i < buffer.size(); ++i)
        {
            if (i >= static_cast<size_t>(combFilterDelay))
            { // Verificar el índice
                buffer[i] += buffer[i - combFilterDelay] * reverbDecay;
            }
        }
    }

    void applyDistortion(std::vector<SAMPLE> &buffer, float gain, float threshold)
    {
        for (auto &sample : buffer)
        {
            sample *= gain;
            if (sample > threshold)
                sample = threshold;
            else if (sample < -threshold)
                sample = -threshold;
        }
    }

    void applyChorus(std::vector<SAMPLE> &buffer, int sampleRate, float depth, float rate)
    {
        const int maxDelay = static_cast<int>(depth * sampleRate); // Retardo máximo basado en la profundidad
        std::vector<SAMPLE> chorusBuffer = buffer;                 // Copia del buffer original para mantener valores originales

        for (size_t i = 0; i < buffer.size(); ++i)
        {
            // Calcular el retardo modulado (delay modulado) usando una onda sinusoidal
            float modulatedDelay = depth * sampleRate * (0.5f * sinf(2.0f * M_PI * rate * i / sampleRate) + 0.5f);
            int delayIndex = static_cast<int>(modulatedDelay);

            if (i >= static_cast<size_t>(delayIndex))
            {
                // Aplicar el efecto chorus mezclando el buffer original con el retrasado
                buffer[i] += chorusBuffer[i - delayIndex] * 0.5f; // Mezclar con el buffer retrasado
            }
        }
    }
};
