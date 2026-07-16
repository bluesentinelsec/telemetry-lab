#include <catch2/catch_test_macros.hpp>

#include <cJSON.h>

#include <memory>
#include <sstream>
#include <string>

#include "model/config.hpp"
#include "model/event.hpp"
#include "view/json_formatter.hpp"

using namespace tmon;

namespace {
struct CjsonDeleter {
  void operator()(cJSON* p) const { cJSON_Delete(p); }
};
using CjsonPtr = std::unique_ptr<cJSON, CjsonDeleter>;

// Parse a single JSONL line (trailing newline is tolerated by cJSON_Parse).
CjsonPtr Parse(const std::string& line) {
  return CjsonPtr(cJSON_Parse(line.c_str()));
}
std::string Str(cJSON* obj, const char* key) {
  cJSON* item = cJSON_GetObjectItem(obj, key);
  return item && item->valuestring ? item->valuestring : "";
}
}  // namespace

TEST_CASE("the meta record carries the command and --meta values", "[json]") {
  std::ostringstream os;
  Config c;
  c.command = {"/bin/id"};
  c.meta = {{"run", "smoke"}};
  JsonFormatter f(os, c);
  f.Begin();

  auto j = Parse(os.str());
  REQUIRE(j);
  REQUIRE(Str(j.get(), "record") == "meta");
  cJSON* cmd = cJSON_GetObjectItem(j.get(), "command");
  REQUIRE(cJSON_GetArraySize(cmd) == 1);
  REQUIRE(std::string(cJSON_GetArrayItem(cmd, 0)->valuestring) == "/bin/id");
  cJSON* meta = cJSON_GetObjectItem(j.get(), "meta");
  REQUIRE(std::string(cJSON_GetObjectItem(meta, "run")->valuestring) == "smoke");
}

TEST_CASE("a syscall event carries kind, nr, name, and hex args", "[json]") {
  std::ostringstream os;
  Config c;
  c.command = {"x"};
  JsonFormatter f(os, c);

  Event e;
  e.kind = EventKind::kSyscall;
  e.syscall_nr = 1;  // write
  e.pid = 5;
  e.comm = "sh";
  e.args[0] = 0xdead;
  f.Handle(e);

  auto j = Parse(os.str());
  REQUIRE(j);
  REQUIRE(Str(j.get(), "record") == "event");
  REQUIRE(Str(j.get(), "kind") == "syscall");
  REQUIRE(Str(j.get(), "syscall") == "write");
  REQUIRE(cJSON_GetObjectItem(j.get(), "nr")->valueint == 1);
  cJSON* args = cJSON_GetObjectItem(j.get(), "args");
  REQUIRE(std::string(cJSON_GetArrayItem(args, 0)->valuestring) == "0xdead");
}

TEST_CASE("the args array is limited to the syscall arity", "[json]") {
  std::ostringstream os;
  Config c;
  c.command = {"x"};
  JsonFormatter f(os, c);

  Event e;
  e.kind = EventKind::kSyscall;
  e.syscall_nr = 3;  // close, arity 1
  e.args = {0x3, 0xdead, 0xbeef, 0, 0, 0};
  f.Handle(e);

  auto j = Parse(os.str());
  REQUIRE(j);
  cJSON* args = cJSON_GetObjectItem(j.get(), "args");
  REQUIRE(cJSON_GetArraySize(args) == 1);
  REQUIRE(std::string(cJSON_GetArrayItem(args, 0)->valuestring) == "0x3");
}

TEST_CASE("a syscall event carries path, result, ok, and errno", "[json]") {
  std::ostringstream os;
  Config c;
  c.command = {"x"};
  JsonFormatter f(os, c);

  Event e;
  e.kind = EventKind::kSyscall;
  e.syscall_nr = 257;  // openat
  e.comm = "cat";
  e.path = "/no/such/file";
  e.path_argno = 1;
  e.has_ret = true;
  e.ret = -1;
  e.error = 2;  // ENOENT
  e.has_duration = true;
  e.duration_ns = 1500;
  f.Handle(e);

  auto j = Parse(os.str());
  REQUIRE(j);
  REQUIRE(Str(j.get(), "path") == "/no/such/file");
  REQUIRE(cJSON_GetObjectItem(j.get(), "ret")->valueint == -1);
  REQUIRE(cJSON_IsFalse(cJSON_GetObjectItem(j.get(), "ok")));
  REQUIRE(Str(j.get(), "error") == "ENOENT");
  REQUIRE(cJSON_GetObjectItem(j.get(), "errno")->valueint == 2);
  REQUIRE(cJSON_GetObjectItem(j.get(), "duration_ns")->valueint == 1500);
}

TEST_CASE("the summary record reports the counts and exit code", "[json]") {
  std::ostringstream os;
  Config c;
  c.command = {"x"};
  JsonFormatter f(os, c);

  Summary sm;
  sm.syscall_events = 3;
  sm.total_events = 4;
  sm.processes = 2;
  sm.target_exit_code = 1;
  f.End(sm);

  auto j = Parse(os.str());
  REQUIRE(j);
  REQUIRE(Str(j.get(), "record") == "summary");
  REQUIRE(cJSON_GetObjectItem(j.get(), "syscall_events")->valueint == 3);
  REQUIRE(cJSON_GetObjectItem(j.get(), "processes")->valueint == 2);
  REQUIRE(cJSON_GetObjectItem(j.get(), "target_exit_code")->valueint == 1);
}
