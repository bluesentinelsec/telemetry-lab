#include <catch2/catch_test_macros.hpp>

#include <cstring>

#include "bpf/tmon_event.h"
#include "core/event_decode.hpp"
#include "model/event.hpp"

using namespace tmon;

TEST_CASE("a syscall wire record decodes field-for-field", "[decode]") {
  tmon_event w{};
  w.kind = TMON_SYSCALL;
  w.ts_ns = 123456;
  w.pid = 10;
  w.tid = 11;
  w.syscall_nr = 59;
  for (int i = 0; i < TMON_SYSCALL_ARGS; i++) w.args[i] = 0x100ULL + i;
  std::strcpy(w.comm, "sh");

  Event e = DecodeEvent(w);
  REQUIRE(e.kind == EventKind::kSyscall);
  REQUIRE(e.ts_ns == 123456);
  REQUIRE(e.pid == 10);
  REQUIRE(e.tid == 11);
  REQUIRE(e.syscall_nr == 59);
  REQUIRE(e.comm == "sh");
  REQUIRE(e.args[0] == 0x100ULL);
  REQUIRE(e.args[5] == 0x105ULL);
}

TEST_CASE("fork/exec/exit kinds and their payloads map", "[decode]") {
  tmon_event w{};

  w.kind = TMON_FORK;
  w.child_pid = 42;
  REQUIRE(DecodeEvent(w).kind == EventKind::kFork);
  REQUIRE(DecodeEvent(w).child_pid == 42);

  w.kind = TMON_EXEC;
  REQUIRE(DecodeEvent(w).kind == EventKind::kExec);

  w.kind = TMON_EXIT;
  w.exit_code = 7;
  Event e = DecodeEvent(w);
  REQUIRE(e.kind == EventKind::kExit);
  REQUIRE(e.exit_code == 7);
}

TEST_CASE("comm is bounded when the kernel field has no terminator",
          "[decode]") {
  tmon_event w{};
  w.kind = TMON_SYSCALL;
  std::memset(w.comm, 'A', TMON_COMM_LEN);  // deliberately not NUL-terminated
  Event e = DecodeEvent(w);
  REQUIRE(e.comm.size() == TMON_COMM_LEN);
  REQUIRE(e.comm == std::string(TMON_COMM_LEN, 'A'));
}
