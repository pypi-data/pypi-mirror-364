from gdm.quantities import Distance

import erad.models.fragility_curve as frag
from erad.enums import AssetTypes

DEFAULT_FLOOD_DEPTH_FRAGILITY_CURVES = frag.HazardFragilityCurves(
    asset_state_param="flood_depth",
    curves=[
        frag.FragilityCurve(
            asset_type=AssetTypes.switch,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.35, "m"), Distance(0.50, "m"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.battery_storage,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.35, "m"), Distance(0.50, "m"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.40, "m"), Distance(1.0, "m"), 1 / 0.40],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.35, "m"), Distance(1.0, "m"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_poles,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.35, "m"), Distance(1.0, "m"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.distribution_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.8, "m"), Distance(1.0, "m"), 1 / 0.8],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.solar_panels,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.35, "m"), Distance(0.6, "m"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.substation,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.40, "m"), Distance(1.0, "m"), 1 / 0.4],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_mad_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.35, "m"), Distance(0.6, "m"), 1 / 0.35],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transformer_pole_mount,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.30, "m"), Distance(0.8, "m"), 1 / 0.3],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_junction_box,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.40, "m"), Distance(1.0, "m"), 1 / 0.40],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_overhead_lines,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.30, "m"), Distance(1.8, "m"), 1 / 0.3],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_tower,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.40, "m"), Distance(2.2, "m"), 1 / 0.40],
            ),
        ),
        frag.FragilityCurve(
            asset_type=AssetTypes.transmission_underground_cables,
            prob_function=frag.ProbabilityFunction(
                distribution="lognorm",
                parameters=[Distance(0.25, "m"), Distance(0.8, "m"), 1 / 0.25],
            ),
        ),
    ],
)
