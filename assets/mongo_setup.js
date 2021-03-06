var sdef = {
    "_id": "timeseries-4",
    "type": "timeseries",
    "applies_to_version": 4,
    "metrics": {
        "cpuuser": {
            "units": "CPU %",
            "description": "CPU User",
            "help": "The average percentage of time spent in CPU user mode. The average is computed over each time interval."
        },
        "l1dloads": {
            "units": "ratio",
            "description": "L1D loads",
            "help": "The ratio of L1D loads to reference clock ticks."
        },
        "membw": {
            "units": "GB/s",
            "description": "Memory bandwidth",
            "help": "The total rate of data transferred to and from main memory. The rate is computed over each time interval. This value is obtained from the hardware counters."
        },
        "simdins": {
            "units": "insts/s",
            "description": "SIMD instructions",
            "help": "The total rate of floating point SIMD instructions reported by the hardware performance counters on the CPU cores on which the job ran. Note that the meaning of this value is hardware-specific so the data should not in general be compared between HPC resources that have different hardware architectures."
        },
        "memused_minus_diskcache": {
            "units": "GB",
            "description": "Memory usage",
            "help": "The total physical memory used by the operating system excluding memory used for caches. This value includes the contribution for <em>all</em> processes including system daemons and all running HPC jobs but does not include the physical memory used by the kernel page and SLAB caches. For HPC resources that use a Linux-based operating system this value is obtained from the <code>meminfo</code> file in sysfs for each numa node (i.e. <code>/sys/devices/system/node/nodeX/meminfo</code>)",
        },
        "ib_lnet": {
            "units": "MB/s",
            "description": "Interconnect MPI traffic",
            "help": "The total rate of data transferred over the parallel interconnect. The rate is computed over each time interval and is the sum of the data sent and received by each node. Some HPC resources also use the interconnect for parallel filesystem traffic; this filesystem traffic is not included in these data."
        },
        "lnet": {
            "units": "MB/s",
            "description": "Parallel Filesystem traffic",
            "help": "The total rate of data transferred to and from the parallel filesystem. The rate is computed over each time interval and is the sum of data sent and received by each node."
        }
    }
};

var summarydef = {
    "_id": "summary-0.9.33",
    "definitions": {
        "cpiref": {
            "documentation": "Number of reference clock ticks per instruction",
            "type": "ratio",
            "unit": "1"
        },
        "mdc": {
            "*": {
                "mds_sync": {
                    "type": "rate",
                    "unit": "/s"
                },
                "mds_getattr": {
                    "type": "rate",
                    "unit": "/s"
                },
                "mds_close": {
                    "type": "rate",
                    "unit": "/s"
                },
                "reqs": {
                    "type": "rate",
                    "unit": "/s"
                },
                "ldlm_cancel": {
                    "type": "rate",
                    "unit": "/s"
                },
                "mds_getxattr": {
                    "type": "rate",
                    "unit": "/s"
                },
                "mds_readpage": {
                    "type": "rate",
                    "unit": "/s"
                },
                "mds_statfs": {
                    "type": "rate",
                    "unit": "/s"
                },
                "mds_getattr_lock": {
                    "type": "rate",
                    "unit": "/s"
                },
                "wait": {
                    "type": "rate",
                    "unit": "us/s"
                }
            }
        },
        "Error": {
            "documentation": "List of the processing errors encountered during job summary creation",
            "type": "metadata"
        },
        "intel_snb_r2pci": {
            "DATA_USED": {
                "type": "rate",
                "unit": "/s"
            },
            "TRANSMITS": {
                "type": "rate",
                "unit": "/s"
            },
            "ADDRESS_USED": {
                "type": "rate",
                "unit": "/s"
            },
            "ACKNOWLEDGED_USED": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "vm": {
            "*": {
                "pswpout": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "kswapd_steal": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgscan_kswapd_normal": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgdeactivate": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgpgin": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "B/s"
                },
                "pageoutrun": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgmajfault": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pswpin": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgsteal_normal": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgfault": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgpgout": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "B/s"
                },
                "pginodesteal": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgscan_direct_normal": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgrotated": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgalloc_normal": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "allocstall": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgactivate": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "slabs_scanned": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgrefill_normal": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "kswapd_inodesteal": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                },
                "pgfree": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/vmstat"
                    },
                    "documentation": "procfs metric read from /proc/vmstat",
                    "type": "rate",
                    "unit": "/s"
                }
            }
        },
        "intel_hsw_qpi": {
            "CTR3": {
                "type": "rate",
                "unit": "flt/s"
            },
            "CTR2": {
                "type": "rate",
                "unit": "flt/s"
            },
            "CTR1": {
                "type": "rate",
                "unit": "flt/s"
            },
            "CTR0": {
                "type": "rate",
                "unit": "flt/s"
            }
        },
        "intel_hsw_cbo": {
            "0": {
                "type": "instant",
                "unit": ""
            }
        },
        "cpldref": {
            "documentation": "Number of clock ticks per L1D cache load using the reference CPU clock.",
            "type": "ratio",
            "unit": "1"
        },
        "cpicore": {
            "documentation": "Number of clock ticks per instruction using the core CPU clock.",
            "type": "ratio",
            "unit": "1"
        },
        "intel_hsw_pcu": {
            "0": {
                "type": "instant",
                "unit": ""
            },
            "C6_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "C3_CYCLES": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "osc": {
            "*": {
                "ost_statfs": {
                    "type": "rate",
                    "unit": "/s"
                },
                "write_bytes": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "ost_setattr": {
                    "type": "rate",
                    "unit": "/s"
                },
                "reqs": {
                    "type": "rate",
                    "unit": "/s"
                },
                "ost_punch": {
                    "type": "rate",
                    "unit": "/s"
                },
                "ost_destroy": {
                    "type": "rate",
                    "unit": "/s"
                },
                "ost_read": {
                    "type": "rate",
                    "unit": "/s"
                },
                "ost_write": {
                    "type": "rate",
                    "unit": "/s"
                },
                "read_bytes": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "wait": {
                    "type": "rate",
                    "unit": "us/s"
                }
            }
        },
        "ib": {
            "*": {
                "port_xmit_wait": {
                    "type": "rate",
                    "unit": "ms/s"
                },
                "local_link_integrity_errors": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_rcv_errors": {
                    "type": "rate",
                    "unit": "/s"
                },
                "excessive_buffer_overrun_errors": {
                    "type": "rate",
                    "unit": "/s"
                },
                "link_downed": {
                    "type": "rate",
                    "unit": "/s"
                },
                "VL15_dropped": {
                    "type": "rate",
                    "unit": "/s"
                },
                "symbol_error": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_rcv_switch_relay_errors": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_xmit_packets": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_rcv_remote_physical_errors": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_xmit_constraint_errors": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_rcv_packets": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_xmit_data": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "port_rcv_constraint_errors": {
                    "type": "rate",
                    "unit": "/s"
                },
                "link_error_recovery": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_rcv_data": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "port_xmit_discards": {
                    "type": "rate",
                    "unit": "/s"
                }
            }
        },
        "intel_wtm": {
            "*": {
                "CLOCKS_UNHALTED_REF": {
                    "type": "rate",
                    "unit": "/s"
                },
                "INSTRUCTIONS_RETIRED": {
                    "type": "rate",
                    "unit": "/s"
                },
                "4395024": {
                    "type": "instant",
                    "unit": ""
                },
                "CLOCKS_UNHALTED_CORE": {
                    "type": "rate",
                    "unit": "/s"
                },
                "4423696": {
                    "type": "instant",
                    "unit": ""
                },
                "4391441": {
                    "type": "instant",
                    "unit": ""
                },
                "4391633": {
                    "type": "instant",
                    "unit": ""
                },
                "4424144": {
                    "type": "instant",
                    "unit": ""
                },
                "4391377": {
                    "type": "instant",
                    "unit": ""
                },
                "4392145": {
                    "type": "instant",
                    "unit": ""
                },
                "4391249": {
                    "type": "instant",
                    "unit": ""
                }
            }
        },
        "ib_sw": {
            "*": {
                "tx_bytes": {
                    "documentation": "Average rate of data transmitted by each compute node. The IB HCA/PORT statistics are obtained by querying the extended performance counters of the switch port to which the HCA/PORT is connected.",
                    "type": "rate",
                    "unit": "B/s"
                },
                "rx_packets": {
                    "documentation": "Average rate of packets received by each compute node. The IB HCA/PORT statistics are obtained by querying the extended performance counters of the switch port to which the HCA/PORT is connected.",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_packets": {
                    "documentation": "Average rate of packets transmitted by each compute node. The IB HCA/PORT statistics are obtained by querying the extended performance counters of the switch port to which the HCA/PORT is connected.",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_bytes": {
                    "documentation": "Average rate of bytes received by each compute node. The IB HCA/PORT statistics are obtained by querying the extended performance counters of the switch port to which the HCA/PORT is connected.",
                    "type": "rate",
                    "unit": "B/s"
                }
            }
        },
        "ps": {
            "*": {
                "processes": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/stat"
                    },
                    "documentation": "procfs metric read from /proc/stat",
                    "type": "rate",
                    "unit": "/s"
                },
                "load_5": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/loadavg"
                    },
                    "documentation": "procfs metric read from /proc/loadavg",
                    "type": "instant",
                    "unit": ""
                },
                "load_1": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/loadavg"
                    },
                    "documentation": "procfs metric read from /proc/loadavg",
                    "type": "instant",
                    "unit": ""
                },
                "load_15": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/loadavg"
                    },
                    "documentation": "procfs metric read from /proc/loadavg",
                    "type": "instant",
                    "unit": ""
                },
                "nr_threads": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/loadavg"
                    },
                    "documentation": "procfs metric read from /proc/loadavg",
                    "type": "instant",
                    "unit": ""
                },
                "ctxt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/stat"
                    },
                    "documentation": "procfs metric read from /proc/stat",
                    "type": "rate",
                    "unit": "/s"
                },
                "nr_running": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/loadavg"
                    },
                    "documentation": "procfs metric read from /proc/loadavg",
                    "type": "instant",
                    "unit": ""
                }
            }
        },
        "intel_snb_imc": {
            "CAS_READS": {
                "type": "rate",
                "unit": "/s"
            },
            "ACT_COUNT": {
                "type": "rate",
                "unit": "/s"
            },
            "PRE_COUNT_MISS": {
                "type": "rate",
                "unit": "/s"
            },
            "CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "CAS_WRITES": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "amd64_sock": {
            "*": {
                "DRAM": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "HT2": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "HT1": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "HT0": {
                    "type": "rate",
                    "unit": "B/s"
                }
            }
        },
        "amd64_core": {
            "*": {
                "DCSF": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "USER": {
                    "type": "rate",
                    "unit": "/s"
                },
                "SSE_FLOPS": {
                    "type": "rate",
                    "unit": "/s"
                }
            }
        },
        "mic": {
            "*": {
                "sys_sum": {
                    "type": "rate",
                    "unit": "cs/s"
                },
                "jiffy_counter": {
                    "type": "rate",
                    "unit": "cs/s"
                },
                "user_sum": {
                    "type": "rate",
                    "unit": "cs/s"
                },
                "idle_sum": {
                    "type": "rate",
                    "unit": "cs/s"
                },
                "nice_sum": {
                    "type": "rate",
                    "unit": "cs/s"
                }
            }
        },
        "intel_ivb_imc": {
            "CTR3": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR2": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR1": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR0": {
                "type": "rate",
                "unit": "/s"
            },
            "FIXED_CTR": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_hsw": {
            "SSE_DOUBLE_PACKED": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_L1D_ALL": {
                "type": "rate",
                "unit": "/s"
            },
            "CLOCKS_UNHALTED_CORE": {
                "type": "rate",
                "unit": "/s"
            },
            "CLOCKS_UNHALTED_REF": {
                "type": "rate",
                "unit": "/s"
            },
            "SSE_DOUBLE_SCALAR": {
                "type": "rate",
                "unit": "/s"
            },
            "SIMD_DOUBLE_256": {
                "type": "rate",
                "unit": "/s"
            },
            "INSTRUCTIONS_RETIRED": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_L2_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_L1_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_LLC_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_ALL": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "nHosts": {
            "documentation": "Number of hosts with raw data",
            "type": "discrete",
            "unit": "1"
        },
        "intel_hsw_hau": {
            "CTR3": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR2": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR1": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR0": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_ivb_r2pci": {
            "CTR3": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR2": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR1": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR0": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "net": {
            "*": {
                "rx_over_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_window_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_aborted_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_compressed": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_carrier_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "collisions": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_packets": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_dropped": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_packets": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_length_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_missed_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_bytes": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "B/s"
                },
                "rx_frame_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_dropped": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_crc_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_bytes": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "B/s"
                },
                "tx_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_fifo_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_fifo_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_heartbeat_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "multicast": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_errors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_compressed": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/class/net/*/statistics"
                    },
                    "documentation": "sysfs metric read from /sys/class/net/*/statistics",
                    "type": "rate",
                    "unit": "/s"
                }
            }
        },
        "proc": {
            "*": {
                "VmHWM": {
                    "type": "instant",
                    "unit": "kB"
                },
                "VmExe": {
                    "type": "instant",
                    "unit": "kB"
                },
                "VmStk": {
                    "type": "instant",
                    "unit": "kB"
                },
                "Uid": {
                    "type": "instant",
                    "unit": ""
                },
                "Mems_allowed_list": {
                    "type": "instant",
                    "unit": ""
                },
                "VmPeak": {
                    "type": "instant",
                    "unit": "kB"
                },
                "VmData": {
                    "type": "instant",
                    "unit": "kB"
                },
                "VmSize": {
                    "type": "instant",
                    "unit": "kB"
                },
                "VmLck": {
                    "type": "instant",
                    "unit": "kB"
                },
                "Threads": {
                    "type": "instant",
                    "unit": ""
                },
                "Cpus_allowed_list": {
                    "type": "instant",
                    "unit": ""
                },
                "VmPTE": {
                    "type": "instant",
                    "unit": "kB"
                },
                "VmLib": {
                    "type": "instant",
                    "unit": "kB"
                },
                "VmRSS": {
                    "type": "instant",
                    "unit": "kB"
                },
                "VmSwap": {
                    "type": "instant",
                    "unit": "kB"
                }
            }
        },
        "llite": {
            "*": {
                "rename": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "osc_read": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "B/s"
                },
                "direct_write": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "B/s"
                },
                "readdir": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "setxattr": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "read_bytes": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "B/s"
                },
                "close": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "flock": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "open": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "osc_write": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "B/s"
                },
                "listxattr": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "mmap": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "removexattr": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "mkdir": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "direct_read": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "B/s"
                },
                "getattr": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "lookup": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "rmdir": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "dirty_pages_misses": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "truncate": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "getxattr": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "dirty_pages_hits": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "inode_permission": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "ioctl": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "link": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "symlink": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "unlink": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "write_bytes": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "B/s"
                },
                "alloc_inode": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "setattr": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "fsync": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "statfs": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "seek": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "mknod": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                },
                "create": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/fs/lustre/llite"
                    },
                    "documentation": "procfs metric read from /proc/fs/lustre/llite",
                    "type": "rate",
                    "unit": "/s"
                }
            }
        },
        "intel_snb_cbo": {
            "LLC_LOOKUP_WRITE": {
                "type": "rate",
                "unit": "/s"
            },
            "RING_IV_USED": {
                "type": "rate",
                "unit": "/s"
            },
            "LLC_LOOKUP_DATA_READ": {
                "type": "rate",
                "unit": "/s"
            },
            "COUNTER0_OCCUPANCY": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_ivb_qpi": {
            "*": {
                "CTR3": {
                    "type": "rate",
                    "unit": "flt/s"
                },
                "CTR2": {
                    "type": "rate",
                    "unit": "flt/s"
                },
                "CTR1": {
                    "type": "rate",
                    "unit": "flt/s"
                },
                "CTR0": {
                    "type": "rate",
                    "unit": "flt/s"
                }
            }
        },
        "complete": {
            "documentation": "Whether the raw data was available for all nodes that the job was assigned",
            "type": "metadata"
        },
        "mem": {
            "Writeback": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "MemTotal": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "FilePages": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "AnonPages": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "HugePages_Free": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": ""
            },
            "Bounce": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "MemFree": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "Inactive": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "PageTables": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "Dirty": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "NFS_Unstable": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "Mapped": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "Active": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "MemUsed": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "Slab": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": "B"
            },
            "HugePages_Total": {
                "source": {
                    "type": "sysfs",
                    "name": "/sys/devices/system/node/node*/meminfo"
                },
                "documentation": "sysfs metric read from /sys/devices/system/node/node*/meminfo",
                "type": "instant",
                "unit": ""
            }
        },
        "intel_uncore": {
            "PMC0": {
                "type": "rate",
                "unit": "/s"
            },
            "PMC1": {
                "type": "rate",
                "unit": "/s"
            },
            "PMC2": {
                "type": "rate",
                "unit": "/s"
            },
            "PMC3": {
                "type": "rate",
                "unit": "/s"
            },
            "PMC4": {
                "type": "rate",
                "unit": "/s"
            },
            "PMC5": {
                "type": "rate",
                "unit": "/s"
            },
            "PMC6": {
                "type": "rate",
                "unit": "/s"
            },
            "PMC7": {
                "type": "rate",
                "unit": "/s"
            },
            "FIXED_CTR0": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_hsw_imc": {
            "CTR3": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR2": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR1": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR0": {
                "type": "rate",
                "unit": "/s"
            },
            "FIXED_CTR": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_snb_pcu": {
            "C3_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "C6_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "MIN_SNOOP_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "MIN_IO_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "MAX_TEMP_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "MAX_POWER_CYCLES": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_snb_hau": {
            "READ_REQUESTS": {
                "type": "rate",
                "unit": "/s"
            },
            "CLOCKTICKS": {
                "type": "rate",
                "unit": "/s"
            },
            "WRITE_REQUESTS": {
                "type": "rate",
                "unit": "/s"
            },
            "IMC_WRITES": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_hsw_r2pci": {
            "CTR3": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR2": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR1": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR0": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_nhm": {
            "*": {
                "CLOCKS_UNHALTED_REF": {
                    "type": "rate",
                    "unit": "/s"
                },
                "INSTRUCTIONS_RETIRED": {
                    "type": "rate",
                    "unit": "/s"
                },
                "4395024": {
                    "type": "instant",
                    "unit": ""
                },
                "CLOCKS_UNHALTED_CORE": {
                    "type": "rate",
                    "unit": "/s"
                },
                "4423696": {
                    "type": "instant",
                    "unit": ""
                },
                "4391441": {
                    "type": "instant",
                    "unit": ""
                },
                "4391633": {
                    "type": "instant",
                    "unit": ""
                },
                "4424144": {
                    "type": "instant",
                    "unit": ""
                },
                "4391377": {
                    "type": "instant",
                    "unit": ""
                },
                "4392145": {
                    "type": "instant",
                    "unit": ""
                },
                "4391249": {
                    "type": "instant",
                    "unit": ""
                }
            }
        },
        "intel_rapl": {
            "*": {
                "MSR_PP0_ENERGY_STATUS": {
                    "type": "rate",
                    "unit": "mJ/s"
                },
                "MSR_PKG_ENERGY_STATUS": {
                    "type": "rate",
                    "unit": "mJ/s"
                },
                "MSR_DRAM_ENERGY_STATUS": {
                    "type": "rate",
                    "unit": "mJ/s"
                }
            }
        },
        "tmpfs": {
            "*": {
                "bytes_used": {
                    "source": {
                        "type": "syscall",
                        "name": "statfs"
                    },
                    "documentation": "syscall metric read from statfs",
                    "type": "instant",
                    "unit": "B"
                },
                "files_used": {
                    "source": {
                        "type": "syscall",
                        "name": "statfs"
                    },
                    "documentation": "syscall metric read from statfs",
                    "type": "instant",
                    "unit": ""
                }
            }
        },
        "FLOPS": {
            "documentation": "Generated from the available FLOPS hardware counters present on the cores",
            "type": "rate",
            "unit": "ops/s"
        },
        "lnet": {
            "*": {
                "rx_bytes_dropped": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/lnet/stats"
                    },
                    "documentation": "procfs metric read from /proc/sys/lnet/stats",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_bytes": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/lnet/stats"
                    },
                    "documentation": "procfs metric read from /proc/sys/lnet/stats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "tx_msgs": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/lnet/stats"
                    },
                    "documentation": "procfs metric read from /proc/sys/lnet/stats",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_msgs": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/lnet/stats"
                    },
                    "documentation": "procfs metric read from /proc/sys/lnet/stats",
                    "type": "rate",
                    "unit": "/s"
                },
                "rx_msgs_dropped": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/lnet/stats"
                    },
                    "documentation": "procfs metric read from /proc/sys/lnet/stats",
                    "type": "rate",
                    "unit": "/s"
                },
                "tx_bytes": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/lnet/stats"
                    },
                    "documentation": "procfs metric read from /proc/sys/lnet/stats",
                    "type": "rate",
                    "unit": "B/s"
                }
            }
        },
        "intel_snb": {
            "SSE_DOUBLE_PACKED": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_L1D_ALL": {
                "type": "rate",
                "unit": "/s"
            },
            "CLOCKS_UNHALTED_CORE": {
                "type": "rate",
                "unit": "/s"
            },
            "CLOCKS_UNHALTED_REF": {
                "type": "rate",
                "unit": "/s"
            },
            "SSE_DOUBLE_SCALAR": {
                "type": "rate",
                "unit": "/s"
            },
            "SIMD_DOUBLE_256": {
                "type": "rate",
                "unit": "/s"
            },
            "INSTRUCTIONS_RETIRED": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_L2_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_L1_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_LLC_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_ALL": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_ivb_pcu": {
            "C3_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "C6_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "MIN_SNOOP_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "MIN_IO_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "MAX_TEMP_CYCLES": {
                "type": "rate",
                "unit": "/s"
            },
            "MAX_POWER_CYCLES": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_snb_qpi": {
            "G1_DRS_DATA": {
                "type": "rate",
                "unit": "/s"
            },
            "TxL_FLITS_G1_SNP": {
                "type": "rate",
                "unit": "/s"
            },
            "TxL_FLITS_G1_HOM": {
                "type": "rate",
                "unit": "/s"
            },
            "G2_NCB_DATA": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "ib_ext": {
            "*": {
                "port_unicast_xmit_pkts": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_multicast_rcv_pkts": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_unicast_rcv_pkts": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_rcv_pkts": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_multicast_xmit_pkts": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_xmit_data": {
                    "type": "rate",
                    "unit": "B/s"
                },
                "port_xmit_pkts": {
                    "type": "rate",
                    "unit": "/s"
                },
                "port_rcv_data": {
                    "type": "rate",
                    "unit": "B/s"
                }
            }
        },
        "intel_ivb_cbo": {
            "LLC_LOOKUP_WRITE": {
                "type": "rate",
                "unit": "/s"
            },
            "RING_IV_USED": {
                "type": "rate",
                "unit": "/s"
            },
            "LLC_LOOKUP_DATA_READ": {
                "type": "rate",
                "unit": "/s"
            },
            "COUNTER0_OCCUPANCY": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "sysv_shm": {
            "*": {
                "mem_used": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sysvipc/shm"
                    },
                    "documentation": "procfs metric read from /proc/sysvipc/shm",
                    "type": "instant",
                    "unit": "B"
                },
                "segs_used": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sysvipc/shm"
                    },
                    "documentation": "procfs metric read from /proc/sysvipc/shm",
                    "type": "instant",
                    "unit": ""
                }
            }
        },
        "nfs": {
            "*": {
                "CREATE_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "MKNOD_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "MKDIR_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "direct_write": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "xprt_sends": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "REMOVE_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "direct_read": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "GETATTR_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "xprt_bad_xids": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READDIRPLUS_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "WRITE_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "GETATTR_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "MKDIR_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "REMOVE_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "READDIRPLUS_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "MKDIR_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "vfs_writepage": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "MKNOD_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "CREATE_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "read_page": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "FSINFO_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "MKNOD_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RMDIR_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "SYMLINK_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "FSINFO_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "setattr_trunc": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "congestion_wait": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "normal_write": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "vfs_fsync": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "CREATE_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LOOKUP_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "vfs_setattr": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READ_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "RMDIR_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "WRITE_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "ACCESS_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "SYMLINK_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "PATHCONF_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "FSSTAT_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "PATHCONF_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "PATHCONF_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "WRITE_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "silly_rename": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "FSINFO_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "WRITE_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "COMMIT_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "REMOVE_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "PATHCONF_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "READDIRPLUS_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "write_page": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "CREATE_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "FSINFO_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "RENAME_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LINK_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "SETATTR_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "xprt_req_u": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READDIRPLUS_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READ_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "normal_read": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "READDIR_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "LINK_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "READLINK_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "GETATTR_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READLINK_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "ACCESS_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RENAME_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "FSSTAT_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "SYMLINK_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "GETATTR_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "inode_revalidate": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "SYMLINK_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "CREATE_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "CREATE_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "vfs_readpages": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "SETATTR_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "FSINFO_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "server_write": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "COMMIT_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "FSINFO_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "vfs_access": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "server_read": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "vfs_flush": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "xprt_recvs": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READLINK_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "WRITE_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "FSSTAT_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "SETATTR_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "SETATTR_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "GETATTR_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "MKNOD_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "FSSTAT_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "FSSTAT_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "CREATE_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "ACCESS_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LOOKUP_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "ACCESS_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "PATHCONF_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "MKNOD_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LOOKUP_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "REMOVE_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "LOOKUP_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "FSSTAT_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "COMMIT_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "short_read": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READDIR_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "vfs_readpage": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READ_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "FSINFO_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "vfs_release": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "MKDIR_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "CREATE_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RMDIR_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "SETATTR_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RENAME_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "GETATTR_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "READDIR_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "COMMIT_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "ACCESS_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "MKDIR_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LINK_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "attr_invalidate": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LOOKUP_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "LOOKUP_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READDIRPLUS_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "SYMLINK_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "LINK_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "data_invalidate": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "MKNOD_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "RMDIR_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READLINK_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READ_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "SETATTR_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "PATHCONF_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "ACCESS_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LINK_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "REMOVE_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READDIR_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "LINK_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "WRITE_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READDIRPLUS_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "SETATTR_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "RMDIR_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READDIRPLUS_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "ACCESS_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "SYMLINK_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LINK_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "SYMLINK_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "LINK_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READDIRPLUS_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "dentry_revalidate": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READLINK_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RMDIR_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "LOOKUP_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "vfs_getdents": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READLINK_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "vfs_lock": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "MKDIR_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RMDIR_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "RENAME_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "vfs_lookup": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "xprt_bklog_u": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "COMMIT_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "COMMIT_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "vfs_writepages": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "extend_write": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "PATHCONF_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "REMOVE_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "COMMIT_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RMDIR_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "MKNOD_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "REMOVE_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READ_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READ_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "MKNOD_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "COMMIT_execute": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "LOOKUP_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "WRITE_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "delay": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READDIR_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RENAME_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "GETATTR_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "MKDIR_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READLINK_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "vfs_open": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READ_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "short_write": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "SETATTR_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "REMOVE_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "MKDIR_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "FSINFO_timeouts": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "RENAME_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "GETATTR_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READDIR_ops": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "ACCESS_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "SYMLINK_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "RENAME_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "FSSTAT_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READDIR_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "READDIR_bytes_sent": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "PATHCONF_queue": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "vfs_updatepage": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "RENAME_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "READ_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                },
                "WRITE_rtt": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "READLINK_bytes_recv": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "B/s"
                },
                "FSSTAT_ntrans": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/self/mountstats"
                    },
                    "documentation": "procfs metric read from /proc/self/mountstats",
                    "type": "rate",
                    "unit": "/s"
                }
            }
        },
        "intel_ivb": {
            "SSE_DOUBLE_PACKED": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_L1D_ALL": {
                "type": "rate",
                "unit": "/s"
            },
            "CLOCKS_UNHALTED_CORE": {
                "type": "rate",
                "unit": "/s"
            },
            "CLOCKS_UNHALTED_REF": {
                "type": "rate",
                "unit": "/s"
            },
            "SSE_DOUBLE_SCALAR": {
                "type": "rate",
                "unit": "/s"
            },
            "SIMD_DOUBLE_256": {
                "type": "rate",
                "unit": "/s"
            },
            "INSTRUCTIONS_RETIRED": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_L2_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_L1_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_LLC_HIT": {
                "type": "rate",
                "unit": "/s"
            },
            "LOAD_OPS_ALL": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "intel_ivb_hau": {
            "CTR3": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR2": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR1": {
                "type": "rate",
                "unit": "/s"
            },
            "CTR0": {
                "type": "rate",
                "unit": "/s"
            }
        },
        "membw": {
            "documentation": "Average rate of data transferred to and from main memory per CPU socket.",
            "type": "rate",
            "unit": "B/s"
        },
        "mpirx": {
            "documentation": "Estimate of the average rate of MPI data received per node over the InfiniBand interface. The estimate is calculated by subtracting the parallel filesystem data from the total InfiniBand data (for the compute resources that use the InfiniBand interconnect for parallel filesystem data).",
            "type": "rate",
            "unit": "B/s"
        },
        "vfs": {
            "*": {
                "inode_use": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/fs/inode-state"
                    },
                    "documentation": "procfs metric read from /proc/sys/fs/inode-state",
                    "type": "instant",
                    "unit": ""
                },
                "dentry_use": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/fs/dentry-state"
                    },
                    "documentation": "procfs metric read from /proc/sys/fs/dentry-state",
                    "type": "instant",
                    "unit": ""
                },
                "file_use": {
                    "source": {
                        "type": "procfs",
                        "name": "/proc/sys/fs/inode-state"
                    },
                    "documentation": "procfs metric read from /proc/sys/fs/inode-state",
                    "type": "instant",
                    "unit": ""
                }
            }
        },
        "cpu": {
            "softirq": {
                "source": {
                    "type": "procfs",
                    "name": "/proc/stat"
                },
                "documentation": "procfs metric read from /proc/stat",
                "type": "rate",
                "unit": "cs/s"
            },
            "iowait": {
                "source": {
                    "type": "procfs",
                    "name": "/proc/stat"
                },
                "documentation": "procfs metric read from /proc/stat",
                "type": "rate",
                "unit": "cs/s"
            },
            "system": {
                "source": {
                    "type": "procfs",
                    "name": "/proc/stat"
                },
                "documentation": "procfs metric read from /proc/stat",
                "type": "rate",
                "unit": "cs/s"
            },
            "idle": {
                "source": {
                    "type": "procfs",
                    "name": "/proc/stat"
                },
                "documentation": "procfs metric read from /proc/stat",
                "type": "rate",
                "unit": "cs/s"
            },
            "user": {
                "source": {
                    "type": "procfs",
                    "name": "/proc/stat"
                },
                "documentation": "procfs metric read from /proc/stat",
                "type": "rate",
                "unit": "cs/s"
            },
            "irq": {
                "source": {
                    "type": "procfs",
                    "name": "/proc/stat"
                },
                "documentation": "procfs metric read from /proc/stat",
                "type": "rate",
                "unit": "cs/s"
            },
            "nice": {
                "source": {
                    "type": "procfs",
                    "name": "/proc/stat"
                },
                "documentation": "procfs metric read from /proc/stat",
                "type": "rate",
                "unit": "cs/s"
            }
        },
        "cpuall": {
            "documentation": "The total recorded CPU core clock ticks per unit time expressed as a percentage. This value should by very close to 100 percent. Discrepencies in this value are typically due to data errors in the monitoring software rather than the problems with the HPC job.",
            "type": "rate",
            "unit": "%"
        },
        "block": {
            "*": {
                "wr_ticks": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "rd_merges": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "/s"
                },
                "wr_merges": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "/s"
                },
                "rd_ticks": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "in_flight": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "instant",
                    "unit": ""
                },
                "wr_sectors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "B/s"
                },
                "wr_ios": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "/s"
                },
                "time_in_queue": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "io_ticks": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "ms/s"
                },
                "rd_sectors": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "B/s"
                },
                "rd_ios": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/block/*/stat"
                    },
                    "documentation": "sysfs metric read from /sys/block/*/stat",
                    "type": "rate",
                    "unit": "/s"
                }
            }
        },
        "numa": {
            "*": {
                "local_node": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/devices/system/node/node*/numastat"
                    },
                    "documentation": "sysfs metric read from /sys/devices/system/node/node*/numastat",
                    "type": "rate",
                    "unit": "/s"
                },
                "interleave_hit": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/devices/system/node/node*/numastat"
                    },
                    "documentation": "sysfs metric read from /sys/devices/system/node/node*/numastat",
                    "type": "rate",
                    "unit": "/s"
                },
                "numa_miss": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/devices/system/node/node*/numastat"
                    },
                    "documentation": "sysfs metric read from /sys/devices/system/node/node*/numastat",
                    "type": "rate",
                    "unit": "/s"
                },
                "other_node": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/devices/system/node/node*/numastat"
                    },
                    "documentation": "sysfs metric read from /sys/devices/system/node/node*/numastat",
                    "type": "rate",
                    "unit": "/s"
                },
                "numa_foreign": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/devices/system/node/node*/numastat"
                    },
                    "documentation": "sysfs metric read from /sys/devices/system/node/node*/numastat",
                    "type": "rate",
                    "unit": "/s"
                },
                "numa_hit": {
                    "source": {
                        "type": "sysfs",
                        "name": "/sys/devices/system/node/node*/numastat"
                    },
                    "documentation": "sysfs metric read from /sys/devices/system/node/node*/numastat",
                    "type": "rate",
                    "unit": "/s"
                }
            }
        }
    },
    "summary_version": "0.9.33"
};

db = db.getSiblingDB("supremm");

var applicableVersion = ["0.9.28", "0.9.30", "0.9.31", "0.9.33"];
var i;
for (i = 0; i < applicableVersion.length; i++) {
    summarydef._id = 'summary-' + applicableVersion[i];
    summarydef.summary_version = applicableVersion[i];
    db.schema.update({_id: summarydef._id}, summarydef, {upsert: true})
}

summarydef._id = 'summary-0.9.34';
summarydef.summary_version = '0.9.34';
summarydef.definitions.maxmem = {
    "documentation": "The maximum ratio of memory used to memory available for the nodes that were assigned to the job. Memory used value is obtained from the MemUsed statistic from the /sys/devices/system/node/node*/numastat file.",
    "type": "instant",
    "unit": "ratio"
};
summarydef.definitions.maxmemminus = {
    "documentation": "The maximum ratio of memory used to memory available for the nodes that were assigned to the job. The memory used value does not include the memory usage from the kernel page and slab caches. The memory statistics are obtained from the /sys/devices/system/node/node*/numastat file.",
    "type": "instant",
    "unit": "ratio"
};

db.schema.update({_id: summarydef._id}, summarydef, {upsert: true})

