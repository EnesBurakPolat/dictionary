#include <windows.h>
#include <string>
#include <map>
#include <fstream>
#include <sstream>
#include <algorithm> //for std::transform
#include <vector>
#include <numeric>

using namespace std;

//Derleme = g++ -o dictionary.exe dictionary.cpp -mwindows

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

multimap<string, string> englishToTurkish;
multimap<string, string> turkishToEnglish;
bool isEnglishToTurkish = false;

void LoadDictionary(const string& filename) {
    ifstream file(filename);
    string line;
    while (getline(file, line)) {
        istringstream iss(line);
        string english, turkish;

        if (getline(iss, english, '=') && getline(iss, turkish)) {
            transform(english.begin(), english.end(), english.begin(), ::tolower);
            transform(turkish.begin(), turkish.end(), turkish.begin(), ::tolower);
            englishToTurkish.insert({english, turkish});
            turkishToEnglish.insert({turkish, english});
        }
    }
}

string Translate(const string& input, bool toEnglish) {
    string lowerInput = input;
    transform(lowerInput.begin(), lowerInput.end(), lowerInput.begin(), ::tolower);

    if (toEnglish) {
        vector<string> results;
        auto range = turkishToEnglish.equal_range(lowerInput);

        for (auto it = range.first; it != range.second; ++it) {
            results.push_back(it->second);
        }

        if (!results.empty()) {
            return accumulate(results.begin(), results.end(), string(),
                [](const string& a, const string& b) {
                    return a.empty() ? b : a + ", " + b;
                });
        }
    } 
    else {
        vector<string> results;
        auto range = englishToTurkish.equal_range(lowerInput);

        for (auto it = range.first; it != range.second; ++it) {
            results.push_back(it->second);
        }

        if (!results.empty()) {
            return accumulate(results.begin(), results.end(), string(),
                [](const string& a, const string& b) {
                    return a.empty() ? b : a + ", " + b;
                });
        }
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
        WS_EX_CLIENTEDGE,
        CLASS_NAME,
        "Dictionary [ENG,TR - TR,ENG]",
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
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
    static HWND hEditInput, hButtonTranslate, hButtonToggle, hEditOutput;

    switch (uMsg) {
        case WM_CREATE:

            hEditInput = CreateWindowExA(0, "EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER, 
                20, 20, 200, 20, hwnd, NULL, NULL, NULL);

            hButtonTranslate = CreateWindowExA(0, "BUTTON", "Cevir", WS_CHILD | WS_VISIBLE, 
                240, 20, 80, 20, hwnd, (HMENU)1, NULL, NULL);

            hButtonToggle = CreateWindowExA(0, "BUTTON", "ENG->TR", WS_CHILD | WS_VISIBLE, 
                330, 20, 80, 20, hwnd, (HMENU)2, NULL, NULL);
                
            hEditOutput = CreateWindowExA(0, "EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_READONLY | ES_MULTILINE | WS_VSCROLL,
                20, 60, 390, 100, hwnd, NULL, NULL, NULL);

            SetWindowTextA(hButtonToggle, isEnglishToTurkish ? "TR->ENG" : "ENG->TR");
            break;

        case WM_COMMAND:
            if (LOWORD(wParam) == 1) {
                char buffer[256];
                GetWindowTextA(hEditInput, buffer, 256);
                string input(buffer);
                string output = Translate(input, isEnglishToTurkish);
                SetWindowTextA(hEditOutput, output.c_str());
            } 
            else if (LOWORD(wParam) == 2) {
                isEnglishToTurkish = !isEnglishToTurkish;
                SetWindowTextA(hButtonToggle, isEnglishToTurkish ? "TR->ENG" : "ENG->TR");
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
