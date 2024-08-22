#include <windows.h>
#include <string>
#include <map>
#include <fstream>
#include <sstream>
#include <algorithm> // for std::transform

using namespace std;

//Derleme = g++ -o dictionary.exe dictionary.cpp -mwindows

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

map<string, string> dictionary;

void LoadDictionary(const string& filename) {
    ifstream file(filename);
    string line;
    while (getline(file, line)) {
        istringstream iss(line); //algoritma
        string english, turkish; //algoritma
        if (getline(iss, english, '=') && getline(iss, turkish)) {
            // Convert to lowercase for case-insensitive matching
            transform(english.begin(), english.end(), english.begin(), ::tolower);
            transform(turkish.begin(), turkish.end(), turkish.begin(), ::tolower);
            dictionary[english] = turkish;
        }
    }
}

string Translate(const string& input, bool toEnglish) {
    string lowerInput = input; //algoritma
    // Convert input to lowercase
    transform(lowerInput.begin(), lowerInput.end(), lowerInput.begin(), ::tolower);
    
    if (toEnglish) {
        for (const auto& pair : dictionary) {
            if (lowerInput == pair.second) return pair.first;
        }
    } else {
        auto it = dictionary.find(lowerInput);
        if (it != dictionary.end()) return it->second;
    }
    return "Ceviri bulunamadi.";
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    LoadDictionary("dictionary.txt");

    const char CLASS_NAME[] = "TranslateWindowClass";
    
    WNDCLASSA wc = {};
    wc.lpfnWndProc   = WindowProc;
    wc.hInstance     = hInstance;
    wc.lpszClassName = CLASS_NAME;

    RegisterClassA(&wc);

    HWND hwnd = CreateWindowExA(
        WS_EX_CLIENTEDGE,          // Add border
        CLASS_NAME,
        "Dictionary [ENG,TR - TR,ENG]",
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX, // Add minimize button
        CW_USEDEFAULT, CW_USEDEFAULT, 500, 200,
        NULL,
        NULL,
        hInstance,
        NULL
    );

    if (hwnd == NULL) return 0;

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    MSG msg = {};
    while (GetMessageA(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }

    return 0;
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    static HWND hEditInput, hButton, hEditOutput;

    switch (uMsg) {
        case WM_CREATE:
            hEditInput = CreateWindowExA(0, "EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER, 
                20, 20, 200, 20, hwnd, NULL, NULL, NULL);
            hButton = CreateWindowExA(0, "BUTTON", "Cevir", WS_CHILD | WS_VISIBLE, 
                240, 20, 80, 20, hwnd, (HMENU)1, NULL, NULL);
            hEditOutput = CreateWindowExA(0, "EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_READONLY, 
                20, 60, 300, 20, hwnd, NULL, NULL, NULL);
            break;

        case WM_COMMAND:
            if (LOWORD(wParam) == 1) {
                char buffer[256];
                GetWindowTextA(hEditInput, buffer, 256);

                string input(buffer);
                string output = Translate(input, false);

                SetWindowTextA(hEditOutput, output.c_str());
            }
            break;

        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;

        default:
            return DefWindowProcA(hwnd, uMsg, wParam, lParam);
    }

    return 0;
}
