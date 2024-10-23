#ifndef APICONTROLLER_H
#define APICONTROLLER_H

#include <iostream>
#include <vector>
#include <string>
#include "httplib/httplib.h"  // Biblioteca httplib para el servidor HTTP
#include "AudioRecorder.cpp"

class ApiController {
public:
    ApiController(int port);
    void start();
    void stop();
    void sendBuffer(const std::vector<float>& buffer);
    
private:
    int port;
    httplib::Server server;  // Servidor HTTP
    AudioRecorder recorder;
    
    void handleStartRequest(const httplib::Request& req, httplib::Response& res);
    void handleStopRequest(const httplib::Request& req, httplib::Response& res);
    
    std::string effect;  // Almacena el efecto actual
    bool recording;
};

#endif // APICONTROLLER_H
