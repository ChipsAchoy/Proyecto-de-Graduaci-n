#include <iostream>
#include <thread>
#include "ApiController.h"


int main() {
    // Iniciar el controlador de API HTTP en un puerto específico
    ApiController apiController(9876);
    std::thread apiThread(&ApiController::start, &apiController);


    while (true) {
        // Este hilo principal puede seguir haciendo otras tareas, mientras
        // el ApiController maneja los comandos HTTP.
    }

    // Esperar que el hilo de la API termine
    apiThread.join();
    return 0;
}
