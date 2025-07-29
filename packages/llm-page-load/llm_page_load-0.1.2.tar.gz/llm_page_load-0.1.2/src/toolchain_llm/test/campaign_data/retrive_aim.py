retrive_aim = [
    {
        "input": {
            "query": " - 团购联合立减和平台立减的规则为:两个活动无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": r"两个活动[\u4e00-\u9fa5]*无法[\u4e00-\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 天天神券和测试立减的规则为:两个活动无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": r"两个活动[\u4e00-\u9fa5]*无法[\u4e00-\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 团特券和批量立减的叠加规则为:两个活动可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": r"两个活动[\u4e00-\u9fa5]*可以[\u4e00-\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 在建立团购联合立减时可以配置是否与平台券叠加\n - 不需要考虑其他优惠活动",
            "rule_type": "stacking"
        },
        "expect": {
            "search": r'单向配置'
        }
    },
    {
        "input": {
            "query": "- 评价券和团购联合立减两个活动可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台立减和闲时立减​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": "平台立减可以配置与平台券互斥，平台券可以配置与平台立减互斥。当其中一方设置了互斥时，二者无法同时使用，默认使用优惠金额更大的优惠。",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "双向配置"
        }
    },
    {
        "input": {
            "query": " - 平台闲时立减和平台券两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 在建立团购联合立减时可以配置是否与商家立减叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "单向配置"
        }
    },
    {
        "input": {
            "query": " - 在建立团购联合立减时可以配置是否与商家券叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "单向配置"
        }
    },
    {
        "input": {
            "query": " - 平台闲时立减和平台立减无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": "- 平台立减和会员卡折扣两个活动可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 团购联合立减和平台立减两个活动无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家立减和医美会员折上折能够相互叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "可以叠加"
        }
    },
    {
        "input": {
            "query": "  - 平台券、平台立减、商家立减三个活动可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台立减和返礼​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台券和商家券​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": "在建立平台立减时可以配置平台立减是否与商家立减叠加。",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "单向配置"
        }
    },
    {
        "input": {
            "query": " - 平台券和会员卡折扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台券和会员日折扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台券和积分抵扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台券和返礼​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": "商家立减可以配置与商家券互斥，商家券可以配置与商家立减互斥。当其中一方设置了互斥时，二者无法同时使用，默认使用优惠金额更大的优惠。",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "双向配置"
        }
    },
    {
        "input": {
            "query": "可以在建立会员卡折扣时配置是否与商家立减同享",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "单向配置"
        }
    },
    {
        "input": {
            "query": " - 平台券和医美会员折上折​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家立减和闲时立减​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": "在建立平台立减时可以配置平台立减是否与商家券叠加。",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "单向配置"
        }
    },
    {
        "input": {
            "query": " - 平台立减和会员日折扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台立减和积分抵扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台立减和医美会员折上折​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台券和闲时立减​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 平台券和商家立减​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家立减和返礼​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 闲时立减和会员日折扣​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 闲时立减和积分抵扣​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 会员日折扣和积分抵扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 会员卡折扣和返礼​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 闲时立减和医美会员折上折​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家券和医美会员折上折​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家券和会员卡折扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家券和会员日折扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家券和积分抵扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 闲时立减和返礼​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家券和返礼​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家立减和会员日折扣​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 闲时立减和会员卡折扣​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 商家立减和积分抵扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 闲时立减和商家券​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 会员卡折扣和医美会员折上折​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 会员卡折扣和会员日折扣​两个活动的优惠无法叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*无法[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 会员卡折扣和积分抵扣​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 返礼和医美会员折上折​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 会员日折扣和医美会员折上折​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 积分抵扣和医美会员折上折​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 会员日折扣和返礼​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": " - 积分抵扣和返礼​两个活动的优惠可以叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "两个活动[\\u4e00-\\u9fa5]*可以[\\u4e00-\\u9fa5]*叠加"
        }
    },
    {
        "input": {
            "query": "- ​测试立减可以配置与团购联合立减互斥，团购联合立减也可以配置与测试立减互斥。\n- 不需要考虑其他优惠活动",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "双向配置"
        }
    },
    {
        "input": {
            "query": " - 医美会员折上折和测试立减可以互相配置是否相互叠加",
            "rule_type": "stacking"
        },
        "expect": {
            "search": "双向配置"
        }
    }
]
