#include <catch2/catch_test_macros.hpp>

#include <sstream>
#include <string>

#include "model/config.hpp"
#include "model/event.hpp"
#include "view/human_formatter.hpp"

using namespace tmon;

namespace {
Config BasicConfig() {
  Config c;
  c.command = {"/bin/true"};
  return c;
}
bool Contains(const std::string& hay, const std::string& needle) {
  return hay.find(needle) != std::string::npos;
}
}  // namespace

TEST_CASE("a syscall line shows the resolved name and hex args", "[human]") {
  std::ostringstream os;
  Config c = BasicConfig();
  HumanFormatter f(os, c);

  Event e;
  e.kind = EventKind::kSyscall;
  e.syscall_nr = 59;  // execve
  e.pid = 7;
  e.comm = "sh";
  e.args[0] = 0x1234;
  f.Handle(e);

  REQUIRE(Contains(os.str(), "execve("));
  REQUIRE(Contains(os.str(), "0x1234"));
}

TEST_CASE("an unknown syscall falls back to a numeric name", "[human]") {
  std::ostringstream os;
  Config c = BasicConfig();
  HumanFormatter f(os, c);

  Event e;
  e.kind = EventKind::kSyscall;
  e.syscall_nr = 8888888;
  f.Handle(e);

  REQUIRE(Contains(os.str(), "syscall_8888888"));
}

TEST_CASE("fork and exit render as annotations", "[human]") {
  std::ostringstream os;
  Config c = BasicConfig();
  HumanFormatter f(os, c);

  Event fork;
  fork.kind = EventKind::kFork;
  fork.child_pid = 99;
  f.Handle(fork);

  Event exit;
  exit.kind = EventKind::kExit;
  exit.exit_code = 3;
  f.Handle(exit);

  REQUIRE(Contains(os.str(), "fork -> child 99"));
  REQUIRE(Contains(os.str(), "exited with 3"));
}

TEST_CASE("summary-only suppresses events but End still prints totals",
          "[human]") {
  std::ostringstream os;
  Config c = BasicConfig();
  c.summary_only = true;
  HumanFormatter f(os, c);

  Event e;
  e.kind = EventKind::kSyscall;
  e.syscall_nr = 0;
  f.Handle(e);
  REQUIRE(os.str().empty());

  Summary sm;
  sm.syscall_events = 5;
  sm.total_events = 6;
  sm.processes = 1;
  f.End(sm);
  REQUIRE(Contains(os.str(), "5 syscalls"));
}

TEST_CASE("quiet suppresses the summary line", "[human]") {
  std::ostringstream os;
  Config c = BasicConfig();
  c.quiet = true;
  HumanFormatter f(os, c);

  Summary sm;
  f.End(sm);
  REQUIRE(os.str().empty());
}
