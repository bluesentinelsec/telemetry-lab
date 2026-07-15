#include "core/meta_parse.hpp"

namespace tmon {

std::optional<std::pair<std::string, std::string>> ParseMetaArg(
    const std::string& token) {
  auto eq = token.find('=');
  if (eq == std::string::npos || eq == 0) return std::nullopt;
  return std::make_pair(token.substr(0, eq), token.substr(eq + 1));
}

}  // namespace tmon
