#include "ApiController.h"


ApiController::ApiController(int port) : port(port), recording(false), effect("noeffect") {
    if (!recorder.initialize()) {
        std::cerr << "Error al inicializar el grabador" << std::endl;
    }
}

void ApiController::start() {
    // Ruta para manejar la señal de inicio de grabación
    server.Post("/start", [this](const httplib::Request& req, httplib::Response& res) {
        this->handleStartRequest(req, res);
    });

    // Ruta para manejar la señal de stop y enviar el buffer
    server.Post("/stop", [this](const httplib::Request& req, httplib::Response& res) {
        this->handleStopRequest(req, res);
    });

    std::cout << "Iniciando servidor HTTP en el puerto " << port << std::endl;
    server.listen("0.0.0.0", port);  // Escuchar en todas las interfaces
}

void ApiController::stop() {
    server.stop();
}

void ApiController::handleStartRequest(const httplib::Request& req, httplib::Response& res) {
    auto body = req.body;
    std::cout << "Body recibido " << req.body << std::endl;
    // Buscar la clave "effect" en el cuerpo
    size_t effect_pos = body.find("\"effect\"");
    
    
    if (effect_pos != std::string::npos) {
        // Encontrar el inicio del valor de "effect"
        size_t colon_pos = body.find(":", effect_pos);
        size_t quote_start = body.find("\"", colon_pos);
        size_t quote_end = body.find("\"", quote_start + 1);

        if (colon_pos != std::string::npos && quote_start != std::string::npos && quote_end != std::string::npos) {
            // Extraer el valor de "effect"
            std::string effect = body.substr(quote_start + 1, quote_end - quote_start - 1);
            std::cout << "Iniciando grabación con efecto: " << effect << std::endl;
            if (effect == "noeffect"){
                effect = "";
            }
            recording = true;
            recorder.startRecording("temp", "mp3", effect);
            // Aquí inicia la grabación con el efecto

            // Enviar respuesta de éxito
            res.set_content("Recording started with effect: " + effect, "text/plain");
        } else {
            // Error si el formato es incorrecto
            res.status = 400;  // Bad request
            res.set_content("Invalid effect format", "text/plain");
        }
    } else {
        // Si no se encontró "effect", retornar un error
        res.status = 400;  // Bad request
        res.set_content("Effect not specified", "text/plain");
    }
}

void ApiController::handleStopRequest(const httplib::Request& req, httplib::Response& res) {
    if (recording) {
        recording = false;
        std::cout << "Deteniendo la grabación..." << std::endl;
        recorder.stopRecording();

        // Obtener el buffer de audio desde el AudioRecorder
        std::vector<float> audioBuffer = recorder.getBuffer();

        // Normalizar el buffer de audio entre -1.0 y 1.0
        for (float& sample : audioBuffer) {
            if (sample > 1.0f) sample = 1.0f;
            if (sample < -1.0f) sample = -1.0f;
        }

        // Convertir el buffer de audio de float a char* (bytes)
        const char* bufferBytes = reinterpret_cast<const char*>(audioBuffer.data());
        size_t bufferSize = audioBuffer.size() * sizeof(float);  // Tamaño total en bytes

        // Establecer el tipo de contenido como binario y enviar el buffer
        res.set_content(bufferBytes, bufferSize, "application/octet-stream");

        std::cout << "Buffer de audio enviado correctamente, tamaño: " << bufferSize << " bytes" << std::endl;
        
        recorder.clearBuffer();
    } else {
        res.status = 400;
        res.set_content("Recording not started", "text/plain");
    }
}


