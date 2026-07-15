// Layer 2 — business logic. Parsing of `--meta KEY=VALUE` arguments. Lives here
// (not inline in the CLI) so the rule "split on the first '='; key must be
// non-empty" is unit-testable without spinning up argument parsing.
#ifndef TMON_CORE_META_PARSE_HPP
#define TMON_CORE_META_PARSE_HPP

#include <optional>
#include <string>
#include <utility>

namespace tmon {

// Parse one KEY=VALUE token. Returns the (key, value) pair, or nullopt if the
// token has no '=' or an empty key. VALUE may be empty and may itself contain
// '=' (only the first one splits).
std::optional<std::pair<std::string, std::string>> ParseMetaArg(
    const std::string& token);

}  // namespace tmon

#endif  // TMON_CORE_META_PARSE_HPP
