// file_io primitive: write a temporary file and read it back.
//
// Uses <fstream> and <filesystem>, which link the C++ standard library
// naturally, so no substrate anchor is needed (unlike the compute-only `empty`).
// std::filesystem::temp_directory_path() is portable across Linux and Windows.
// Exercises the file-I/O telemetry family; always exits 0 on success.
#include <filesystem>
#include <fstream>
#include <string>

int main() {
    const auto path = std::filesystem::temp_directory_path() / "ttp_file_io.dat";

    {
        std::ofstream out(path, std::ios::binary | std::ios::trunc);
        if (!out) {
            return 1;
        }
        out << "telemetry-lab\n";
    }
    {
        std::ifstream in(path, std::ios::binary);
        if (!in) {
            return 1;
        }
        const std::string content((std::istreambuf_iterator<char>(in)),
                                  std::istreambuf_iterator<char>());
        if (content.empty()) {
            return 1;
        }
    }

    std::error_code ec;
    std::filesystem::remove(path, ec);
    return 0;
}
