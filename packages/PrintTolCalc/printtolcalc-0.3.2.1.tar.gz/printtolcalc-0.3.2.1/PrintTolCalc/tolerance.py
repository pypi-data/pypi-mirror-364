# SPDX-License-Identifier: LicenseRef-OQL-1.2

import math


def calculate_tolerance(expected, measured):
    tolerances = {}

    for axis, e, m in zip(["X", "Y", "Z"], expected, measured):
        for label, value in [("expected", e), ("measured", m)]:
            if math.isnan(value):
                raise ValueError(
                    f"{label.capitalize()} value for {axis}-axis cannot be NaN."
                )
            if math.isinf(value):
                raise ValueError(
                    f"{label.capitalize()} value for {axis}-axis cannot be infinite."
                )
            if value == 0:
                raise ValueError(
                    f"{label.capitalize()} value for {axis}-axis cannot be zero."
                )
            if value < 0:
                raise ValueError(
                    f"{label.capitalize()} value for {axis}-axis cannot be negative."
                )

        def decimal_places(n):
            if isinstance(n, float):
                s = f"{n:.10f}".rstrip("0")
                if "." in s:
                    return len(s.split(".")[1])
            return 0

        if decimal_places(e) > 2 or decimal_places(m) > 2:
            print(
                f"Warning: {label.capitalize()} value for {axis}-axis input has more than 2 decimal places. "
                f"This is not recommended for floating point accuracy reasons. "
                f"Decimal places after the second are only handled in the percentage calculation and may be inaccurate."
            )

        signed = ((float(m) - float(e)) / float(e)) * 100
        absolute = abs(signed)
        tolerances[axis] = {"signed": signed, "absolute": absolute}

    return tolerances
