// SPDX-License-Identifier: Apache-2.0
#include <sinsp_with_test_input.h>
#include <libsinsp/metrics_collector.h>

TEST_F(sinsp_with_test_input, OpenEntryUnreadablePathKeepsPairAndExitPath) {
    add_default_init_thread();
    open_inspector();
    const auto stats = m_inspector.get_sinsp_stats_v2();
    ASSERT_NE(stats, nullptr);
    const auto before = stats->m_n_retrieve_evts_drops;
    add_filtered_event_advance_ts(increasing_ts(), INIT_TID, PPME_SYSCALL_OPEN_E, 3,
                         empty_value<char*>(), uint32_t(PPM_O_RDONLY), uint32_t(0));
    auto evt = add_event_advance_ts(increasing_ts(), INIT_TID, PPME_SYSCALL_OPEN_X, 6,
                                    int64_t(5), "/etc/shadow", uint32_t(PPM_O_RDONLY),
                                    uint32_t(0), uint32_t(0), uint64_t(42));
    ASSERT_EQ(stats->m_n_retrieve_evts_drops, before);
    ASSERT_EQ(get_field_as_string(evt, "fd.name"), "/etc/shadow");
    ASSERT_EQ(get_field_as_string(evt, "evt.is_open_read"), "true");
}

TEST_F(sinsp_with_test_input, MissingOpenEntryStillCountsAsRetrievalFailure) {
    add_default_init_thread();
    open_inspector();
    const auto stats = m_inspector.get_sinsp_stats_v2();
    const auto before = stats->m_n_retrieve_evts_drops;
    add_event_advance_ts(increasing_ts(), INIT_TID, PPME_SYSCALL_OPEN_X, 6,
                         int64_t(5), "/etc/shadow", uint32_t(PPM_O_RDONLY),
                         uint32_t(0), uint32_t(0), uint64_t(42));
    ASSERT_EQ(stats->m_n_retrieve_evts_drops, before + 1);
}

TEST_F(sinsp_with_test_input, OpenEntryPathStillOverridesChangedExitPath) {
    add_default_init_thread();
    open_inspector();
    add_filtered_event_advance_ts(increasing_ts(), INIT_TID, PPME_SYSCALL_OPEN_E, 3,
                         "/etc/shadow", uint32_t(PPM_O_RDONLY), uint32_t(0));
    auto evt = add_event_advance_ts(increasing_ts(), INIT_TID, PPME_SYSCALL_OPEN_X, 6,
                                    int64_t(5), "/tmp/changed", uint32_t(PPM_O_RDONLY),
                                    uint32_t(0), uint32_t(0), uint64_t(42));
    ASSERT_EQ(get_field_as_string(evt, "fd.name"), "/etc/shadow");
}

TEST_F(sinsp_with_test_input, CreatEntryUnreadablePathKeepsPairAndExitPath) {
    add_default_init_thread();
    open_inspector();
    const auto stats = m_inspector.get_sinsp_stats_v2();
    const auto before = stats->m_n_retrieve_evts_drops;
    add_filtered_event_advance_ts(increasing_ts(), INIT_TID, PPME_SYSCALL_CREAT_E, 2,
                         empty_value<char*>(), uint32_t(0644));
    auto evt = add_event_advance_ts(increasing_ts(), INIT_TID, PPME_SYSCALL_CREAT_X, 6,
                                    int64_t(5), "/var/log/lab_clear.log", uint32_t(0644),
                                    uint32_t(0), uint64_t(42), uint16_t(0));
    ASSERT_EQ(stats->m_n_retrieve_evts_drops, before);
    ASSERT_EQ(get_field_as_string(evt, "fd.name"), "/var/log/lab_clear.log");
}
