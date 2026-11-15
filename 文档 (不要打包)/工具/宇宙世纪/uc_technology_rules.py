"""UC-only folds of selected side content into the retained mainline technologies.

Original era packages are read-only inputs. Entire-plan merges preserve their
unlock roster, while additions list only the expressly requested units.
"""

ADDITIONS = {
    'EFSF_0079': {
        'Tech_EFSF_0079_T2_Luna2TechnologyIntegrationPlan': ['FA_78_1'],
        'Tech_EFSF_0079_T2_GLineDevelopmentPlan': ['RX_78_7', 'FA_78_3'],
        'Tech_EFSF_0079_T2_GMKaiDevelopmentPlan': ['RGM_79FP', 'RGM_79FD'],
    },
    'ZEON_0079': {
        'Tech_ZEON_0079_GroundTypeMSDevelopmentPlan': ['MS_07H'],
    },
    'TITANS_0087': {
        'Tech_TITANS_0087_MarasaiDevelopmentPlan': ['RMS_106CS', 'RMS_119'],
    },
    'NEO_ZEON_0087': {
        'Tech_NEO_ZEON_0087_GyanKaiDevelopmentPlan': ['MS_14J'],
    },
}

# faction, destination mainline technology, source side technology, exclusions
MERGES = [
    ('ZEON_0079', 'Tech_ZEON_0079_ZakuIILateTypeDevelopmentPlan', 'Tech_ZEON_0079_ApsarasDevelopmentPlan', []),
    ('ZEON_0079', 'Tech_ZEON_0079_T2_NextGenerationMainstayMSBiddingPlan', 'Tech_ZEON_0079_T2_UnderwaterMADevelopmentPlan', []),
    ('ZEON_0079', 'Tech_ZEON_0079_T2_UnitedMaintenancePlan', 'Tech_ZEON_0079_T2_HygoggDevelopmentPlan', ['EMS_10F']),
    ('AEUG_0087', 'Tech_AEUG_0087_T2_ZZGundamDevelopmentPlan', 'Tech_AEUG_0087_T2_SGundamDevelopmentPlan', []),
    ('AEUG_0087', 'Tech_AEUG_0087_T2_NouvelGMIIIDevelopmentPlan', 'Tech_AEUG_0087_T2_EXSGundamDevelopmentPlan', []),
    ('TITANS_0087', 'Tech_TITANS_0087_ByarlantDevelopmentPlan', 'Tech_TITANS_0087_PsycoGundamDevelopmentPlan', []),
    ('TITANS_0087', 'Tech_TITANS_0087_T2_SpaceTypeTMSDevelopmentPlan', 'Tech_TITANS_0087_T2_PsycoGundamMK2DevelopmentPlan', []),
]

REMOVED_UNITS = {'MS_15A', 'EMS_10F'}
REMOVED_TECHNOLOGIES = {'Tech_ZEON_0079_T2_GyanPowerfulPlan'}


def additions_for(faction, sections):
    result = {tech: list(units) for tech, units in ADDITIONS.get(faction, {}).items()}
    for owner, target, source, exclusions in MERGES:
        if owner != faction:
            continue
        values = sections['hiddenAction_' + source + '_UnlockUnit']['alsoTriggerAction']
        units = [call.strip()[7:] for call in values.split(',') if call.strip().startswith('Unlock_')]
        result.setdefault(target, []).extend(unit for unit in units if unit not in exclusions)
    return {tech: list(dict.fromkeys(unit for unit in units if unit not in REMOVED_UNITS)) for tech, units in result.items()}
