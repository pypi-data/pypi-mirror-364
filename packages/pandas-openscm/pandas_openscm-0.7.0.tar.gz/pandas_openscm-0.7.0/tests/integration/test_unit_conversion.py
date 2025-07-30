"""
Integration tests of `pandas_openscm.unit_conversion`
"""

from __future__ import annotations

import re
import sys
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from pandas_openscm.exceptions import MissingOptionalDependencyError
from pandas_openscm.index_manipulation import (
    set_index_levels_func,
)
from pandas_openscm.testing import assert_frame_alike, create_test_df
from pandas_openscm.unit_conversion import (
    AmbiguousTargetUnitError,
    MissingDesiredUnitError,
    convert_unit,
    convert_unit_from_target_series,
    convert_unit_like,
)

check_auto_index_casting_df = pytest.mark.parametrize(
    "only_two_index_levels_df",
    (
        pytest.param(True, id="only_two_index_levels"),
        pytest.param(False, id="more_than_two_index_levels"),
    ),
)
"""
Parameterisation to use to check handling of auto casting to `pd.Index`

This casting causes all sorts of indexing and other issues.
This parameterisation ensures that we check this edge case.
"""


@check_auto_index_casting_df
def test_convert_unit_no_op(only_two_index_levels_df):
    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=2,
        n_runs=3,
        timepoints=np.array([1.0, 2.0, 3.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    res = convert_unit(
        start, start.index.to_frame()["unit"].reset_index("unit", drop=True)
    )

    pd.testing.assert_frame_equal(res, start)


def test_convert_unit_unknown_mapping_type():
    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=2,
        n_runs=3,
        timepoints=np.array([1.0, 2.0, 3.0]),
    )

    with pytest.raises(NotImplementedError, match="DataFrame"):
        convert_unit(
            start,
            # DataFrame not supported, has to be Series
            start.index.to_frame()[["unit"]].reset_index("unit", drop=True),
        )


@check_auto_index_casting_df
@pytest.mark.parametrize(
    "unit, exp_unit",
    (
        pytest.param(None, "unit", id="default"),
        ("units", "units"),
    ),
)
def test_convert_unit_single_unit(unit, exp_unit, only_two_index_levels_df):
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=2,
        n_runs=3,
        timepoints=np.array([1.0, 2.0, 3.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    call_kwargs = {}
    if unit is not None:
        start = (
            start.reset_index("unit")
            .rename({"unit": unit}, axis="columns")
            .set_index(unit, append=True)
        )
        call_kwargs["unit_level"] = unit

    res = convert_unit(start, "K", **call_kwargs)

    assert (res.index.get_level_values(exp_unit) == "K").all()

    np.testing.assert_equal(
        res.loc[res.index.get_level_values("variable") == "Cold", :].values,
        1e-3 * start.loc[start.index.get_level_values("variable") == "Cold", :].values,
    )

    np.testing.assert_equal(
        res.loc[res.index.get_level_values("variable") == "Warm", :].values,
        1e3 * start.loc[start.index.get_level_values("variable") == "Warm", :].values,
    )

    np.testing.assert_equal(
        res.loc[res.index.get_level_values("variable") == "Body temperature", :].values,
        273.15
        + start.loc[
            start.index.get_level_values("variable") == "Body temperature", :
        ].values,
    )


def test_convert_unit_ur_injection():
    pint = pytest.importorskip("pint")

    start = create_test_df(
        variables=[("Wavelength", "m")],
        n_scenarios=2,
        n_runs=2,
        timepoints=np.array([1.0, 2.0, 3.0]),
    )

    # Without injection, raises
    with pytest.raises(pint.DimensionalityError):
        convert_unit(start, "Hz")

    # With injection and context, all good
    ur = pint.UnitRegistry()
    with ur.context("spectroscopy"):
        res = convert_unit(start, "Hz", ur=ur)

    np.testing.assert_allclose(
        res.values,
        2.998 * 1e8 / start.values,
        rtol=1e-4,
    )


@check_auto_index_casting_df
def test_convert_unit_mapping(only_two_index_levels_df):
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("temperature", "K"),
            ("erf", "W / m^2"),
            ("ohc", "ZJ"),
        ],
        n_scenarios=2,
        n_runs=2,
        timepoints=np.array([1850.0, 2000.0, 2050.0, 2100.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    # Don't convert W / m^2
    res = convert_unit(start, {"K": "degC", "ZJ": "J"})

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "temperature", :].values,
        -273.15
        + start.loc[
            start.index.get_level_values("variable") == "temperature", :
        ].values,
    )

    np.testing.assert_equal(
        res.loc[res.index.get_level_values("variable") == "erf", :].values,
        start.loc[start.index.get_level_values("variable") == "erf", :].values,
    )

    np.testing.assert_equal(
        res.loc[res.index.get_level_values("variable") == "ohc", :].values,
        1e21 * start.loc[start.index.get_level_values("variable") == "ohc", :].values,
    )


@check_auto_index_casting_df
def test_convert_series(only_two_index_levels_df):
    pytest.importorskip("pint")

    # Check that conversion works if user supplies a Series of target units
    start = create_test_df(
        variables=[
            ("temperature", "K"),
            ("erf", "W / m^2"),
            ("ohc", "ZJ"),
        ],
        n_scenarios=2,
        n_runs=2,
        timepoints=np.array([1850.0, 2000.0, 2050.0, 2100.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    desired_units = (
        start.loc[start.index.get_level_values("variable") != "temperature"]
        .reset_index("unit")["unit"]
        .replace({"W / m^2": "ZJ / yr / m^2", "ZJ": "PJ"})
    )

    res = convert_unit(start, desired_units)

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "temperature", :].values,
        start.loc[start.index.get_level_values("variable") == "temperature", :].values,
    )

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "erf", :].values,
        (60.0 * 60.0 * 24.0 * 365.25)
        * 1e-21
        * start.loc[start.index.get_level_values("variable") == "erf", :].values,
    )

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "ohc", :].values,
        1e6 * start.loc[start.index.get_level_values("variable") == "ohc", :].values,
    )


@check_auto_index_casting_df
def test_convert_series_all_rows(only_two_index_levels_df):
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("temperature", "K"),
            ("erf", "W / m^2"),
            ("ohc", "ZJ"),
        ],
        n_scenarios=2,
        n_runs=2,
        timepoints=np.array([1850.0, 2000.0, 2050.0, 2100.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    desired_units = start.reset_index("unit")["unit"].replace(
        {"W / m^2": "ZJ / yr / m^2", "ZJ": "PJ"}
    )

    res = convert_unit(start, desired_units)

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "temperature", :].values,
        start.loc[start.index.get_level_values("variable") == "temperature", :].values,
    )

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "erf", :].values,
        (60.0 * 60.0 * 24.0 * 365.25)
        * 1e-21
        * start.loc[start.index.get_level_values("variable") == "erf", :].values,
    )

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "ohc", :].values,
        1e6 * start.loc[start.index.get_level_values("variable") == "ohc", :].values,
    )


@check_auto_index_casting_df
def test_convert_series_extra_rows(only_two_index_levels_df):
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("temperature", "K"),
            ("erf", "W / m^2"),
            ("ohc", "ZJ"),
        ],
        n_scenarios=2,
        n_runs=2,
        timepoints=np.array([1850.0, 2000.0, 2050.0, 2100.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    desired_units = start.reset_index("unit")["unit"].replace(
        {"W / m^2": "ZJ / yr / m^2", "ZJ": "PJ"}
    )
    # Extra rows that aren't in start, should be ignored and not cause failures
    if only_two_index_levels_df:
        desired_units.loc[("carbon")] = "GtC"

    else:
        desired_units.loc[("scenario_2", "temperature", 0)] = "kK"

    res = convert_unit(start, desired_units)

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "temperature", :].values,
        start.loc[start.index.get_level_values("variable") == "temperature", :].values,
    )

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "erf", :].values,
        (60.0 * 60.0 * 24.0 * 365.25)
        * 1e-21
        * start.loc[start.index.get_level_values("variable") == "erf", :].values,
    )

    np.testing.assert_allclose(
        res.loc[res.index.get_level_values("variable") == "ohc", :].values,
        1e6 * start.loc[start.index.get_level_values("variable") == "ohc", :].values,
    )


@check_auto_index_casting_df
def test_convert_unit_like_no_op(only_two_index_levels_df):
    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=2,
        n_runs=3,
        timepoints=np.array([1.0, 2.0, 3.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    res = convert_unit_like(start, start)

    pd.testing.assert_frame_equal(res, start)


check_auto_index_casting_target = pytest.mark.parametrize(
    "only_two_index_levels_target",
    (
        pytest.param(True, id="only_two_index_levels"),
        pytest.param(False, id="more_than_two_index_levels"),
    ),
)
"""
Parameterisation to use to check handling of auto casting to `pd.Index`

This casting causes all sorts of indexing and other issues.
This parameterisation ensures that we check this edge case.
"""


@check_auto_index_casting_df
@check_auto_index_casting_target
def test_convert_unit_like(
    only_two_index_levels_df,
    only_two_index_levels_target,
):
    pytest.importorskip("pint")

    create_kwargs = dict(
        n_scenarios=2,
        n_runs=3,
        timepoints=np.array([1.0, 2.0, 3.0]),
    )
    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        **create_kwargs,
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    target = create_test_df(
        variables=[
            ("Cold", "microK"),
            ("Warm", "MK"),
            ("Body temperature", "degF"),
        ],
        **create_kwargs,
    )
    if only_two_index_levels_target:
        target = target.loc[
            (target.index.get_level_values("scenario") == "scenario_0")
            & (target.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    res = convert_unit_like(start, target)

    exp = convert_unit(start, {"mK": "microK", "kK": "MK", "degC": "degF"})

    assert_frame_alike(res, exp)


@check_auto_index_casting_df
@check_auto_index_casting_target
def test_convert_unit_like_missing_levels(
    only_two_index_levels_df,
    only_two_index_levels_target,
):
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=1,
        n_runs=2,
        timepoints=np.array([2020.0, 2030.0, 2040.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    target = create_test_df(
        variables=[
            ("Cold", "K"),
            ("Warm", "K"),
            ("Body temperature", "degF"),
        ],
        n_scenarios=1,
        n_runs=1,
        timepoints=np.array([1.0, 2.0, 3.0]),
    ).reset_index("run", drop=True)
    if only_two_index_levels_target:
        target = target.reset_index("scenario", drop=True)

    res = convert_unit_like(start, target)

    exp = convert_unit(start, {"mK": "K", "kK": "K", "degC": "degF"})

    assert_frame_alike(res, exp)


@check_auto_index_casting_df
@check_auto_index_casting_target
def test_convert_unit_like_missing_specs(
    only_two_index_levels_df,
    only_two_index_levels_target,
):
    """
    Test conversion when the target doesn't specify a unit for all rows in start
    """
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=1,
        n_runs=2,
        timepoints=np.array([2020.0, 2030.0, 2040.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    target = create_test_df(
        variables=[
            ("Cold", "K"),
            # ("Warm", "K"),
            ("Body temperature", "degF"),
        ],
        n_scenarios=1,
        n_runs=1,
        timepoints=np.array([1.0, 2.0, 3.0]),
    ).reset_index("run", drop=True)
    if only_two_index_levels_target:
        target = target.reset_index("scenario", drop=True)

    res = convert_unit_like(start, target)

    exp = convert_unit(start, {"mK": "K", "degC": "degF"})

    assert_frame_alike(res, exp)


@check_auto_index_casting_df
@check_auto_index_casting_target
def test_convert_unit_like_extra_levels_ok(
    only_two_index_levels_df,
    only_two_index_levels_target,
):
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=1,
        n_runs=2,
        timepoints=np.array([2020.0, 2030.0, 2040.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    target = set_index_levels_func(
        create_test_df(
            variables=[
                ("Cold", "K"),
                ("Warm", "K"),
                ("Body temperature", "degF"),
            ],
            n_scenarios=1,
            n_runs=1,
            timepoints=np.array([1.0, 2.0, 3.0]),
        ).reset_index("run", drop=True),
        {"model": "ma"},
    )
    if only_two_index_levels_target:
        target = target.reset_index("scenario", drop=True)

    res = convert_unit_like(start, target)

    exp = convert_unit(start, {"mK": "K", "kK": "K", "degC": "degF"})

    assert_frame_alike(res, exp)


@check_auto_index_casting_df
@check_auto_index_casting_target
def test_convert_unit_like_extra_levels_ambiguous_error(
    only_two_index_levels_df,
    only_two_index_levels_target,
):
    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=1,
        n_runs=2,
        timepoints=np.array([2020.0, 2030.0, 2040.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    target = pd.DataFrame(
        np.arange(3 * 6).reshape((6, 3)),
        columns=np.array([1.0, 10.0, 100.0]),
        index=pd.MultiIndex.from_tuples(
            [
                ("ma", "scenario_0", "Cold", "microK"),
                ("mb", "scenario_0", "Cold", "K"),
                ("ma", "scenario_0", "Warm", "K"),
                ("mb", "scenario_0", "Warm", "K"),
                ("ma", "scenario_0", "Body temperature", "K"),
                ("mb", "scenario_0", "Body temperature", "degF"),
            ],
            names=["model", "scenario", "variable", "unit"],
        ),
    )
    if only_two_index_levels_target:
        target = target.loc[
            ~(
                (target.index.get_level_values("model") == "ma")
                & (target.index.get_level_values("variable") == "Warm")
            ),
            :,
        ].reset_index(["model", "scenario"], drop=True)

    with pytest.raises(AmbiguousTargetUnitError):
        convert_unit_like(start, target)


@check_auto_index_casting_df
@check_auto_index_casting_target
def test_convert_unit_like_extra_specs(
    only_two_index_levels_df,
    only_two_index_levels_target,
):
    """
    Test conversion when the target has a unit for rows that aren't in start
    """
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("Cold", "mK"),
            ("Warm", "kK"),
            ("Body temperature", "degC"),
        ],
        n_scenarios=1,
        n_runs=2,
        timepoints=np.array([2020.0, 2030.0, 2040.0]),
    )
    if only_two_index_levels_df:
        start = start.loc[
            (start.index.get_level_values("scenario") == "scenario_0")
            & (start.index.get_level_values("run") == 0)
        ].reset_index(["scenario", "run"], drop=True)

    target = create_test_df(
        variables=[
            ("Cold", "K"),
            ("Warm", "K"),
            ("Body temperature", "degF"),
            ("Hot", "PK"),
        ],
        n_scenarios=1,
        n_runs=1,
        timepoints=np.array([1.0, 2.0, 3.0]),
    ).reset_index("run", drop=True)
    if only_two_index_levels_target:
        target = target.reset_index("scenario", drop=True)

    res = convert_unit_like(start, target)

    exp = convert_unit(start, {"mK": "K", "kK": "K", "degC": "degF"})

    assert_frame_alike(res, exp)


def test_convert_unit_like_ur_injection():
    # Importing openscm_units makes the test noticeably slow, hmm
    openscm_units = pytest.importorskip("openscm_units")
    pint = pytest.importorskip("pint")

    start = create_test_df(
        variables=[
            ("emissions_co2", "Mt CO2/yr"),
            ("emissions_n2o", "kt N2O/yr"),
        ],
        n_scenarios=3,
        n_runs=6,
        timepoints=np.array([1.0, 2.0, 3.0]),
    )

    target = create_test_df(
        variables=[
            ("emissions_co2", "Gt C / yr"),
            ("emissions_n2o", "Mt N2ON / yr"),
        ],
        n_scenarios=1,
        n_runs=1,
        timepoints=np.array([1.0, 2.0, 3.0]),
    ).reset_index(["scenario", "run"], drop=True)

    # Without injection, raises
    with pytest.raises(pint.UndefinedUnitError):
        convert_unit_like(start, target)

    # With injection and context, all good
    with openscm_units.unit_registry.context("N2O_conversions"):
        res = convert_unit_like(start, target, ur=openscm_units.unit_registry)

        exp = convert_unit(
            start,
            {"Mt CO2/yr": "Gt C / yr", "kt N2O/yr": "Mt N2ON / yr"},
            ur=openscm_units.unit_registry,
        )

    assert_frame_alike(res, exp)


@pytest.mark.parametrize(
    "df_unit_level, df_unit_level_exp, target_unit_level, target_unit_level_exp",
    (
        pytest.param(None, "unit", None, "unit", id="default"),
        pytest.param("units", "units", None, "units", id="target-inferred-from-df"),
        pytest.param("units", "units", "unit", "unit", id="target-df-differ"),
        pytest.param(None, "unit", "units", "units", id="target-specified-only"),
    ),
)
def test_convert_unit_like_unit_level_handling(
    df_unit_level, df_unit_level_exp, target_unit_level, target_unit_level_exp
):
    pytest.importorskip("pint")

    start = create_test_df(
        variables=[(f"variable_{i}", "kg") for i in range(2)],
        n_scenarios=2,
        n_runs=2,
        timepoints=np.array([1.0, 2.0, 3.0]),
    )

    target = create_test_df(
        variables=[(f"variable_{i}", "g") for i in range(2)],
        n_scenarios=2,
        n_runs=2,
        timepoints=np.array([10.0, 11.0, 12.0]),
    )

    call_kwargs = {}
    if df_unit_level is not None:
        start = (
            start.reset_index("unit")
            .rename({"unit": df_unit_level}, axis="columns")
            .set_index(df_unit_level, append=True)
        )
        call_kwargs["df_unit_level"] = df_unit_level

        if target_unit_level is not None:
            target = (
                target.reset_index("unit")
                .rename({"unit": target_unit_level}, axis="columns")
                .set_index(target_unit_level, append=True)
            )
            call_kwargs["target_unit_level"] = target_unit_level

        else:
            target = (
                target.reset_index("unit")
                .rename({"unit": df_unit_level}, axis="columns")
                .set_index(df_unit_level, append=True)
            )

    elif target_unit_level is not None:
        target = (
            target.reset_index("unit")
            .rename({"unit": target_unit_level}, axis="columns")
            .set_index(target_unit_level, append=True)
        )
        call_kwargs["target_unit_level"] = target_unit_level

    res = convert_unit_like(start, target, **call_kwargs)

    exp = convert_unit(start, "g", unit_level=df_unit_level_exp)

    assert_frame_alike(res, exp)


def test_convert_unit_from_target_series_missing_desired_unit_error():
    start = pd.DataFrame(
        np.arange(2 * 3).reshape((2, 3)),
        columns=np.array([1.0, 10.0, 100.0]),
        index=pd.MultiIndex.from_tuples(
            [
                ("ma", "Cold", "microK"),
                ("mb", "Cold", "K"),
            ],
            names=["model", "variable", "unit"],
        ),
    )

    desired_unit = pd.Series(
        [
            "K",
            # "K",
        ],
        index=pd.MultiIndex.from_tuples(
            [
                ("ma", "Cold"),
                # ("mb", "Cold"),
            ],
            names=["model", "variable"],
        ),
    )

    with pytest.raises(MissingDesiredUnitError):
        convert_unit_from_target_series(start, desired_unit)


def test_convert_unit_from_target_series_no_pint_error():
    start = pd.DataFrame(
        np.arange(2 * 3).reshape((2, 3)),
        columns=np.array([1.0, 10.0, 100.0]),
        index=pd.MultiIndex.from_tuples(
            [
                ("ma", "Cold", "microK"),
                ("mb", "Cold", "K"),
            ],
            names=["model", "variable", "unit"],
        ),
    )

    desired_unit = pd.Series(
        ["K", "K"],
        index=pd.MultiIndex.from_tuples(
            [
                ("ma", "Cold"),
                ("mb", "Cold"),
            ],
            names=["model", "variable"],
        ),
    )

    with patch.dict(sys.modules, {"pint": None}):
        with pytest.raises(
            MissingOptionalDependencyError,
            match=re.escape(
                "`convert_unit_from_target_series(..., ur=None, ...)` "
                "requires pint to be installed"
            ),
        ):
            convert_unit_from_target_series(start, desired_unit)
