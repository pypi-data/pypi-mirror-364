from typing import List, Optional, Union
import numpy as np
import pandas as pd
import pyomo.environ as pyomo
from math import pi, sqrt

from .base import ComponentModel


class PumpedStorageHydropower(ComponentModel):
    """Model representation of a pumped storage hydropower (PSH) plant

    Hydroelectric energy storage system in which water is pumped between
    two reservoirs at different elevation (lower reservoir to an upper
    reservoir), hence raising the potential energy of the transported
    water. Power is generated when water moves from the upper to
    lower reservoir (discharging) and is turned into electrical energy
    by turbines. Power is required to pump water back to the upper
    reservoir (charging).

    Energy balance is expressed to model this system, in which Bernoulli's
    equation are assumed + some pipe losses.

    TODO: Take into account potential additional losses - could be a
    fixed percentage we increase the required power with and decreace
    the generated power
    """

    def __init__(
        self,
        *args,
        # Difference in elevation between the inlet and outlet point
        # of the lower and upper reservoir
        height_difference_inlet_outlet: float,  # in m
        # Characteristics of the pipe
        pipe_diameter: Optional[float] = None,  # in m
        pipe_length: Optional[float] = None,  # in m
        # Geometric properties of upper reservoir = cylindrical shape
        radius_upper_reservoir: float,  # in m
        max_height_upper_reservoir: float,  # in m
        # Geometric properties of lower reservoir = cylindrical shape
        radius_lower_reservoir: Optional[float] = None,  # in m
        max_height_lower_reservoir: Optional[float] = None,  # in m
        # Height difference measured between surface of completely full
        # reservoirs
        number_of_pumps: int = 1,
        number_of_turbines: int = 1,
        # Characteristics of the pump(s) (charging)
        # In case of one pump - with multiple operation points
        pump_flows: Optional[list[float]] = [],
        # In case of multiple pumps
        min_pump_flow: float,  # in m3/s
        max_pump_flow: float,  # in m3/s
        BEP_pump_power: float,  # in W
        BEP_pump_flow: float,  # in m3/s
        max_pump_power: float,  # in W
        # Characteristics of the turbine(s) (discharging)
        # In case of one turbine - with multiple operation points
        turbine_flows: Optional[List[float]] = [],
        # In case of multiple turbines
        min_turbine_flow: float,  # in m3/s
        max_turbine_flow: float,  # in m3/s
        BEP_turbine_power: float,  # in W
        BEP_turbine_flow: float,  # in m3/s
        max_turbine_power: float,  # in W
        # Efficiency of the pumps (charging) and turbines (discharging)
        eta_pump: Union[float, List[float]] = 0.8,
        eta_turbine: Union[float, List[float]] = 0.8,
        # Use a piecewise profile or continious for the calculation
        discrete_pump_operation_points: bool = True,
        discrete_turbine_operation_points: bool = False,
        **kwargs,
    ):
        """Init PumpedStorageHydropower

        This function initialises a Pumped Storage Hydropower (PSH) plant
        by setting various geometrical and hydraulic properties.

        Open system : in an open system, in which the lower reservoir is
        assumed to be an infinite big water body of which the height
        doesn't change when discharging from the upper reservoir, the args
        for the lower reservoir can be set to `None`.

        Closed system : it is required to set both the geometric
        properties for the upper and lower reservoir.

        The pumps are assumed to operate at their Best Efficiency Point
        (BEP), at which a minimal amount of flow seperation, turbulence
        and other losses is expected.

        Args:
          height_difference_inlet_outlet (float): The difference in
          elevation between the inlet and outlet point of the lower and upper
          reservoir, in m
          pipe_diameter (Optional[float]): The diameter of the pipe
          connecting the two reservoirs in m
          pipe_length (Optional[float]): Length of the pipe between the
          reservoirs
          radius_upper_reservoir (float): Radius of the upper reservoir in m
          max_height_upper_reservoir (float): The maximum height of the
          upper reservoir in m
          radius_lower_reservoir (Optional[float]): Radius of the lower
          reservoir in m
          max_height_lower_reservoir (Optional[float]): The maximum height
          of the lower reservoir in m
          number_of_pumps (int): The number of pumps,. Defaults to 1
          number_of_turbines (int): The number of turbines,. Defaults to 1
          pump_flows (Optional[list[float]]): A discrete set of operating
          points at which level the flow can be set, Defaults to `None`,
          min_pump_flow (float): The minimum flow rate of the pump in m3/s
          max_pump_flow (float): The maximum flow rate of the pump in m3/s
          BEP_pump_power (float): The power of the pump at its best
          efficiency point (BEP), in W
          BEP_pump_flow (float): The flow rate at which the pump is most
          efficient, in m3/s
          max_pump_power (float): The maximum power of the pump, in W
          turbine_flows (Optional[list[float]]): A discrete set of operating
          points at which level the flow can be set, Defaults to `None`
          min_turbine_flow (float): The minimum flow rate of the turbine
          in m3/s
          max_turbine_flow (float): The maximum flow rate of the turbine
          in m3/s
          BEP_turbine_power (float): The power of the turbine at its best
          efficiency point (BEP), in W
          BEP_turbine_flow (float): The flow rate at which the turbine is
          most efficient, in m3/s
          max_turbine_power (float): The maximum power of the turbine, in W
          eta_pump (float | list[float]): The efficiency of the pump
          eta_turbine (float | list[float]): The efficiency of the turbine
          discrete_pump_operation_points (bool): Whether the pump should be
          modelled as a discrete set op operation points, defaults to
          True
          discrete_turbine_operation_points (bool): Whether the turbine
          should be modelled as a discrete set op operation points, defaults
          to False
        """
        super().__init__(*args, **kwargs)

        # A stepwise flow rate, in which the efficiency
        # is given for every step is only implemented for 1 pump
        if number_of_pumps != 1 and type(eta_pump) == list:
            raise NotImplementedError("""
                A constant efficiency is required when multiple pumps are 
                configured. It's assumed the pumps will run at their Best
                Efficiency Point (BEP) if multiple pumps are configured.
            """)
        if number_of_pumps != 1 and len(pump_flows) > 1:
            raise NotImplementedError("""
                Multiple operating points for 1 pump (`pump_flows`). 
                cannot be used for multiple pumps. In the case of multiple
                pumps, it's assumed each pump will run at their Best
                Efficiency Point (BEP).
            """)
        if type(pump_flows) is list and type(eta_pump) is list:
            assert len(pump_flows) == len(
                eta_pump
            ), """
                The amount of operation points (read "length") of the
                flow and efficiency of the pumps should be equal.
                Therefor `len(pump_flows) == len(eta_pump)`
            """

        # A stepwise flow rate, in which the efficiency
        # is given for every step is only implemented for 1 turbine
        if number_of_turbines != 1 and type(eta_turbine) == list:
            raise NotImplementedError("""
                A constant efficiency is required when multiple turbines are 
                configured. It's assumed the turbines will run at their Best
                Efficiency Point (BEP) if multiple pumps are configured.
            """)
        if number_of_turbines != 1 and len(turbine_flows) > 1:
            raise NotImplementedError("""
                Multiple operating points for 1 turbine (`turbine_flows`). 
                cannot be used for multiple turbines. In the case of multiple
                turbines, it's assumed each turbine will run at their Best
                Efficiency Point (BEP).
            """)
        if type(turbine_flows) is list and type(eta_turbine) is list:
            assert len(turbine_flows) == len(
                eta_turbine
            ), """
                The amount of operation points (read "length") of the
                flow and efficiency of the turbines should be equal.
                Therefor `len(turbine_flows) == len(eta_turbine)`
            """

        # TODO: Currently the levels are set as multiples of the max pump
        # flow, however, wouldn't it be better to only allow multiples of
        # the BEP point? Because at that level, the pump operates at it most
        # efficient point, and if we would have implemented an exact copy of
        # what's happening in a real pump, than the optimiser would always
        # chose something as close as possible to this point? However, if
        # excess energy is available, we should use it at it's full potetials,
        # so it can be true that, the hydraulic storage at full potential,
        # just using all energy avaible, but running at less efficient
        # pump state, is worth more than running at its most efficient level
        # at a lower flow

        # When not supplied, set the flow to max flow (only 1 setpoint)
        pump_flows = pump_flows or [max_pump_flow]
        turbine_flows = turbine_flows or [max_turbine_flow]

        # Currently, in a multi pump setup, no operation levels can be set
        # meaning the pump is working NOT or AT IT'S FULL POTENTIAL (=MAX)
        # TODO: Add the possibility to set operation point in a multi pump setup
        pump_flow_levels = (
            pump_flows
            if number_of_pumps == 1
            else np.arange(1, number_of_pumps + 1) * max_pump_flow
        )

        # Currently, in a multi turbine setup, no operation levels can be set
        # meaning the turbine is working NOT or AT IT'S FULL POTENTIAL (=MAX)
        # TODO: Add the possibility to set operation point in a multi turbine setup
        turbine_flow_levels = (
            turbine_flows
            if number_of_turbines == 1
            else np.arange(1, number_of_turbines + 1) * max_turbine_flow
        )

        self.pump_index = range(number_of_pumps)
        self.turbine_index = range(number_of_turbines)

        rho = 1e3  # kg/m3
        gravity = 9.81  # N/kg
        max_speed_fluid = 2  # m/s
        kinematic_viscocity_water = 1e-6  # m2/s @ 20°

        # Characteristics of the pipe
        self.pipe_area = (
            (pipe_diameter**2 * pi / 4)
            if pipe_diameter
            else max(pump_flow_levels[-1], turbine_flow_levels[-1]) / max_speed_fluid
        )

        # Check if laminar flow is possible at max capacity
        if pipe_diameter is not None:
            assert (
                pump_flow_levels[-1] / self.pipe_area <= max_speed_fluid + 1e-4
            ), """
                Pipe diameter is to small to assume laminar flow when the pumping
                installation is working at it's full potential (max flow). Laminar
                flow is necessary to make sure the losses inside the pipe are 
                linearly varying with the speed of the fluid.
            """
            assert (
                turbine_flow_levels[-1] / self.pipe_area <= max_speed_fluid + 1e-4
            ), """
                Pipe diameter is to small to assume laminar flow when the turbine
                installation is working at it's full potential (max flow). Laminar
                flow is necessary to make sure the losses inside the pipe are 
                linearly varying with the speed of the fluid.
            """

        self.pipe_diameter = pipe_diameter or sqrt(4 * self.pipe_area / pi)
        self.pipe_length = pipe_length or height_difference_inlet_outlet
        # Constant to calculate pipe losses = K x q (flow) - in J/kg s
        self.K_pipe_losses = (
            32
            * kinematic_viscocity_water
            * self.pipe_length
            / (self.pipe_diameter**2)
            / self.pipe_area
        )

        # Upper reservoir geometry definition - Cylindrical shape
        self.radius_upper_reservoir = radius_upper_reservoir
        self.max_height_upper_reservoir = max_height_upper_reservoir
        self.area_upper_reservoir = radius_upper_reservoir**2 * pi
        self.volume_upper_reservoir = (
            self.area_upper_reservoir * self.max_height_upper_reservoir
        )
        # Lower reservoir geometry definition - Cylindrical shape
        self.radius_lower_reservoir = radius_lower_reservoir or 0
        self.max_height_lower_reservoir = max_height_lower_reservoir or 0
        self.area_lower_reservoir = radius_lower_reservoir**2 * pi
        self.volume_lower_reservoir = (
            self.area_lower_reservoir * self.max_height_lower_reservoir
        )
        # The head is defined as the elevation difference between the
        # inlet and the outlet of the pipe between the reservoirs
        self.height_difference_inlet_outlet = height_difference_inlet_outlet
        self.height_min = (
            self.height_difference_inlet_outlet - self.max_height_lower_reservoir
        )
        self.height_max = (
            self.height_difference_inlet_outlet + self.max_height_upper_reservoir
        )

        # Pump characteristics
        self.number_of_pumps = number_of_pumps
        self.min_pump_flow = min_pump_flow
        self.BEP_pump_flow = BEP_pump_flow
        self.max_pump_flow = max_pump_flow
        self.BEP_pump_power = BEP_pump_power
        self.pump_flow_levels = pump_flow_levels

        # Turbine characteristics
        self.number_of_turbines = number_of_turbines
        self.min_turbine_flow = min_turbine_flow
        self.BEP_turbine_flow = BEP_turbine_flow
        self.max_turbine_flow = max_turbine_flow
        self.BEP_turbine_power = BEP_turbine_power
        self.turbine_flow_levels = turbine_flow_levels

        if type(eta_pump) == list:
            # Efficiency is set for every flow/power level
            self.K_pump = rho * gravity * (1.0 / np.array(eta_pump))
        else:
            self.K_pump = rho * gravity * (1.0 / eta_pump)

        if type(eta_turbine) == list:
            # Efficiency is set for every flow/power level
            self.K_turbine = rho * gravity * np.array(eta_turbine)
        else:
            self.K_turbine = rho * gravity * eta_turbine

        # Method of operation - continious flow allowed or discrete
        # number of operation points
        self.discrete_pump_operation_points = discrete_pump_operation_points
        self.discrete_turbine_operation_points = discrete_turbine_operation_points

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [
            self.namespace("height_upper_reservoir"),
            self.namespace("height_lower_reservoir"),
        ]

        # PARAMETERS

        # Initial head
        # Upper reservoir is assumed to be empty if not initialised
        self.add_parameter(
            "height_upper_reservoir_ini",
            initialize=lambda m: ini.get(self.namespace("height_upper_reservoir"), 0),
            doc=(
                "Initial elevation of water surface above outlet point in upper"
                " reservoir, (m)"
            ),
        )
        # Lower reservoir is assumed to be completely filled if not initialised
        self.add_parameter(
            "height_lower_reservoir_ini",
            initialize=lambda m: ini.get(
                self.namespace("height_lower_reservoir"),
                self.max_height_lower_reservoir,
            ),
            doc=(
                "Initial elevation of water surface above inlet point in upper"
                " reservoir, (m)"
            ),
        )

        # PUMPS
        # Pump model parameters
        if self.discrete_pump_operation_points:
            """Operation at a DISCRETE set of CONTROL POINTS"""
            self.add_parameter(
                "pump_flow_levels_par",
                self.model.i,
                self.pump_index,
                initialize=lambda m, i, j: self.pump_flow_levels[j],
                domain=pyomo.NonNegativeReals,
                doc="Pump water flow levels, (m3/s)",
            )
        else:
            """Operation at CONTINIOUS range of setpoints within BOUNDS"""
            self.add_parameter(
                "pump_flow_max",
                initialize=lambda m: self.number_of_pumps * self.max_pump_flow,
                doc="Maximum of the total pump flow, (m3/s)",
            )
            self.add_parameter(
                "pump_flow_min",
                initialize=lambda m: self.min_pump_flow,
                doc="Minimum of the total pump power, (m3/s)",
            )

        # TURBINES
        # Turbine model parameters
        if self.discrete_turbine_operation_points:
            """Operation at a DISCRETE set of CONTROL POINTS"""
            self.add_parameter(
                "turbine_flow_levels_par",
                self.model.i,
                self.turbine_index,
                initialize=lambda m, i, j: self.turbine_flow_levels[j],
                domain=pyomo.NonNegativeReals,
                doc="Turbine water flow levels, (m3/s)",
            )
        else:
            """Operation at CONTINIOUS range of setpoints within BOUNDS"""
            self.add_parameter(
                "turbine_flow_max",
                initialize=lambda m: self.number_of_turbines * self.max_turbine_flow,
                doc="Maximum of the total turbine flow, (m3/s)",
            )
            self.add_parameter(
                "turbine_flow_min",
                initialize=lambda m: self.min_turbine_flow,
                doc="Minimum the total turbine flow, (m3/s)",
            )

        # VARIABLES

        # The height and SOC, which are closely related
        self.add_variable(
            "height",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.height_difference_inlet_outlet - self.max_height_lower_reservoir,
                self.height_difference_inlet_outlet + self.max_height_upper_reservoir,
            ),
            initialize=(
                ini.get(self.namespace("height_upper_reservoir"), 0)
                + self.height_difference_inlet_outlet
                - ini.get(
                    self.namespace("height_lower_reservoir"),
                    self.max_height_lower_reservoir,
                )
            ),
            doc="Height/elevation used inside the energy calculation (head), (m)",
        )
        self.add_variable(
            "height_upper_reservoir",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.max_height_upper_reservoir),
            doc=(
                "Height off the top surface above the outlet of the upper"
                " reservoir, (m)"
            ),
        )
        self.add_variable(
            "height_lower_reservoir",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.max_height_lower_reservoir),
            doc=(
                "Height of the top surface above the outlet of the lower reservoir, (m)"
            ),
        )
        self.add_variable(
            "SOC",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, 1),
            initialize=ini.get(self.namespace("height_upper_reservoir"), 0)
            / self.max_height_upper_reservoir,
            doc="State of charge hydroelectrical storage, (-)",
        )

        # PUMPS
        # Pump related variables - flow and power are unknown
        if self.discrete_pump_operation_points:
            """Operation at a DISCRETE set of CONTROL POINTS"""
            self.add_variable(
                "pump_flow_binary",
                self.model.i,
                self.pump_index,
                domain=pyomo.Binary,
                initialize=0,
                bounds=(0, 1),
                doc="""Binary variables (Special ordered set of type 1) indicating pump flow level: [1], [2], [3] and [4]""",
            )
            # Power is defined because it's calculated as a product between a
            # binary variable `pump_flow_binary`, which represents the setpoint
            # to be activated and the `head`, a continous variable.
            self.add_variable(
                "pump_power_add_vars",
                self.model.i,
                self.pump_index,
                domain=pyomo.NonNegativeReals,
                initialize=0.0,
                doc="Pump power levels, (W)",
            )

        # General variables
        self.add_variable(
            "pump_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Pump water flow, (m3/s)",
        )

        self.add_variable(
            "pump_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Pump power, (W)",
        )

        # TURBINES
        # Turbine related variables
        if self.discrete_turbine_operation_points:
            """Operation at a DISCRETE set of CONTROL POINTS"""
            self.add_variable(
                "turbine_flow_binary",
                self.model.i,
                self.turbine_index,
                domain=pyomo.Binary,
                initialize=0,
                bounds=(0, 1),
                doc=(
                    "Binary variables (Special ordered set of type 1) indicating"
                    " turbine flow level: [1], [2], [3]"
                ),
            )
            # Power is defined because it's calculated as a product between a
            # binary variable `turbine_flow_binary`, which represents the setpoint
            # to be activated and the `head`, a continous variable.
            self.add_variable(
                "turbine_power_add_vars",
                self.model.i,
                self.turbine_index,
                domain=pyomo.NonNegativeReals,
                initialize=0.0,
                doc="Turbine power levels, (W)",
            )

        # General variables
        self.add_variable(
            "turbine_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Turbine water flow, (m3/s)",
        )
        self.add_variable(
            "turbine_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Tubine power, (W)",
        )

        # The net power requested/produced by the system
        # consumption = positive power = system asks for power - charging
        # production = negative power = system delivers power - discharging
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )

        # The state of the model, if it's charging or not
        self.add_variable(
            "charging",
            self.model.i,
            initialize=0,
            domain=pyomo.Binary,
        )
        self.add_variable(
            "discharging",
            self.model.i,
            initialize=0,
            domain=pyomo.Binary,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        # TODO: Update the modulation part of the model because now, it's
        # assumed every pump/turbine is working at the same state, for
        # example at 50% of their max flow rate.

        # The height and SOC, which are closely related
        self.add_constraint(
            "constraint_height_upper_reservoir_ini",
            rule=lambda m: self.height_upper_reservoir[0]
            == self.height_upper_reservoir_ini,
            doc="Initial height upper reservoir calculation",
        )
        self.add_constraint(
            "constraint_height_lower_reservoir_ini",
            rule=lambda m: self.height_lower_reservoir[0]
            == self.height_lower_reservoir_ini,
            doc="Initial height lower reservoir calculation",
        )
        self.add_constraint(
            "constraint_height",
            self.model.i,
            rule=lambda m, i: self.height[i]
            == self.height_difference_inlet_outlet
            + self.height_upper_reservoir[i]
            - self.height_lower_reservoir[i],
            doc=(
                "Calculation of the height from the level of the upper and lower"
                " reservoir"
            ),
        )
        # CONSTRAINT HEIGHT
        self.add_constraint(
            "constraint_height_upper_reservoir",
            self.model.i,
            rule=lambda m, i: (
                self.area_upper_reservoir
                * (self.height_upper_reservoir[i + 1] - self.height_upper_reservoir[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.pump_flow[i] - self.turbine_flow[i]
                if i + 1 < len(m.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_height_lower_reservoir",
            self.model.i,
            rule=lambda m, i: (
                -self.area_lower_reservoir
                * (self.height_lower_reservoir[i + 1] - self.height_lower_reservoir[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.pump_flow[i] - self.turbine_flow[i]
                if i + 1 < len(m.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_SOC",
            self.model.i,
            rule=lambda m, i: self.SOC[i]
            == self.height_upper_reservoir[i] / self.max_height_upper_reservoir,
        )

        # PUMPS
        if self.discrete_pump_operation_points:
            """Operation at a DISCRETE set of CONTROL POINTS"""
            # Only one operation point/level can be selected, additionally
            # this should be in relation with its charging state
            self.add_constraint(
                "constraint_pump_flow_binary_and_charging",
                self.model.i,
                rule=lambda m, i: self.charging[i]
                == sum(self.pump_flow_binary[i, j] for j in self.pump_index),
                doc=(
                    "Constraint the number of control points that can be activated,"
                    " possible values [0, 1]"
                ),
            )
            self.add_constraint(
                "constraint_pump_flow_rate",
                self.model.i,
                rule=lambda m, i: (
                    self.pump_flow[i]
                    == sum(
                        self.pump_flow_binary[i, j] * self.pump_flow_levels_par[i, j]
                        for j in self.pump_index
                    )
                ),
                doc="water flow in pumps, [m3/s]",
            )
            # A set of 4 additional constrainst are set to deal with the
            # linearisation of a product of a binary variable (x) with a
            # continious variable (y). The product is replaced by another
            # variable (z = x * y) with some additional constraints.
            self.add_constraint(
                "constraint_pump_power_1",
                self.model.i,
                self.pump_index,
                rule=lambda m, i, j: self.pump_power_add_vars[i, j]
                <= self.pump_flow_binary[i, j]
                * self.pump_flow_levels_par[i, j]
                * self.K_pump
                * self.height_max,
                doc=(
                    "1st constraint - pump power is less or equal to the maximum"
                    " possible pump power (max head)"
                ),
            )
            self.add_constraint(
                "constraint_pump_power_2",
                self.model.i,
                self.pump_index,
                rule=lambda m, i, j: self.pump_power_add_vars[i, j]
                <= self.pump_flow_levels_par[i, j] * self.K_pump * self.height[i],
                doc=(
                    "2nd constraint - pump power is less or equal than product between"
                    " flow and water height"
                ),
            )
            self.add_constraint(
                "constraint_pump_power_3",
                self.model.i,
                self.pump_index,
                rule=lambda m, i, j: self.pump_power_add_vars[i, j]
                >= self.pump_flow_levels_par[i, j] * self.K_pump * self.height[i]
                - (1 - self.pump_flow_binary[i, j])
                * self.pump_flow_levels_par[i, j]
                * self.K_pump
                * self.height_max,
                doc="3rd constraint - Additional complex constraint",
            )
            self.add_constraint(
                "constraint_pump_power_4",
                self.model.i,
                self.pump_index,
                rule=lambda m, i, j: self.pump_power_add_vars[i, j] >= 0,
                doc="4th constraint - pump power should be higher than 0",
            )
            # The total power required for the pump
            self.add_constraint(
                "constraint_pump_power_tot",
                self.model.i,
                rule=lambda m, i: self.pump_power[i]
                == sum(
                    self.pump_power_add_vars[i, j]
                    + (
                        self.K_pipe_losses
                        * self.pump_flow_binary[i, j]
                        * self.pump_flow_levels_par[i, j]
                    )
                    for j in self.pump_index
                ),
                doc="Pump power, (W)",
            )
        else:
            """Operation at CONTINIOUS range of setpoints within BOUNDS"""
            self.add_constraint(
                "constraint_pump_flow_max_modulating",
                self.model.i,
                rule=lambda m, i: self.pump_flow[i]
                <= self.charging[i] * self.pump_flow_max[i],
                doc="Pump power, (W)",
            )
            self.add_constraint(
                "constraint_pump_flow_min_modulating",
                self.model.i,
                rule=lambda m, i: self.pump_flow[i]
                >= self.charging[i] * self.pump_flow_min[i],
                doc="Pump power, (W)",
            )
            # The total power required for the pump
            self.add_constraint(
                "constraint_pump_power_modulating",
                self.model.i,
                rule=lambda m, i: self.pump_power[i]
                == self.number_of_pumps
                * self.BEP_pump_power
                * (self.pump_flow[i] / self.BEP_pump_flow)
                + self.K_pipe_losses * self.pump_flow[i],
                doc="water modulating flow, [m3/s]",
            )

        # TURBINES
        if self.discrete_turbine_operation_points:
            """Operation at a DISCRETE set of CONTROL POINTS"""
            # Only one operation point/level can be selected, additionally
            # this should be in relation with its charging state
            self.add_constraint(
                "constraint_turbine_flow_binary_and_discharging",
                self.model.i,
                rule=lambda m, i: self.discharging[i]
                == sum(self.turbine_flow_binary[i, j] for j in self.turbine_index),
                doc=(
                    "Constraint the number of control points that can be activated,"
                    " possible values [0, 1]"
                ),
            )
            self.add_constraint(
                "constraint_turbine_flow_rate",
                self.model.i,
                rule=lambda m, i: self.turbine_flow[i]
                == sum(
                    self.turbine_flow_binary[i, j] * self.turbine_flow_levels_par[i, j]
                    for j in self.turbine_index
                ),
                doc="water flow in pumps, [m3/s]",
            )
            # A set of 4 additional constrainst are set to deal with the
            # linearisation of a product of a binary variable (x) with a
            # continious variable (y). The product is replaced by another
            # variable (z = x * y) with some additional constraints.
            self.add_constraint(
                "constraint_turbine_power_1",
                self.model.i,
                self.turbine_index,
                rule=lambda m, i, j: self.turbine_power_add_vars[i, j]
                <= self.turbine_flow_binary[i, j]
                * self.turbine_flow_levels_par[i, j]
                * self.K_turbine
                * self.height_max,
                doc="1st constraint - turbine power the maximum possible pump power",
            )
            self.add_constraint(
                "constraint_turbine_power_2",
                self.model.i,
                self.turbine_index,
                rule=lambda m, i, j: self.turbine_power_add_vars[i, j]
                <= self.turbine_flow_levels_par[i, j] * self.K_turbine * self.height[i],
                doc=(
                    "2nd constraint - turbine power is less than product between flow"
                    " and water height"
                ),
            )
            self.add_constraint(
                "constraint_turbine_power_3",
                self.model.i,
                self.turbine_index,
                rule=lambda m, i, j: self.turbine_power_add_vars[i, j]
                >= self.turbine_flow_levels_par[i, j] * self.K_turbine * self.height[i]
                - (1 - self.turbine_flow_binary[i, j])
                * self.turbine_flow_levels_par[i, j]
                * self.K_turbine
                * self.height_max,
                doc="3rd constraint - Additional complex constraint",
            )
            self.add_constraint(
                "constraint_turbine_power_4",
                self.model.i,
                self.turbine_index,
                rule=lambda m, i, j: self.turbine_power_add_vars[i, j] >= 0,
                doc="4th constraint - turbine power should be higher than 0",
            )
            # The total power required for the turbine
            self.add_constraint(
                "constraint_turbine_power_tot",
                self.model.i,
                rule=lambda m, i: self.turbine_power[i]
                == sum(
                    self.turbine_power_add_vars[i, j]
                    + (
                        self.K_pipe_losses
                        * self.turbine_flow_binary[i, j]
                        * self.turbine_flow_levels_par[i, j]
                    )
                    for j in self.turbine_index
                ),
                doc="Turbine power, (W)",
            )
        else:
            """Operation at CONTINIOUS range of setpoints within BOUNDS"""
            self.add_constraint(
                "constraint_turbine_flow_max_modulating",
                self.model.i,
                rule=lambda m, i: self.turbine_flow[i]
                <= self.discharging[i] * self.turbine_flow_max,
                doc="Maximum turbine flow constraint",
            )
            self.add_constraint(
                "constraint_turbine_flow_min_modulating",
                self.model.i,
                rule=lambda m, i: self.turbine_flow[i]
                >= self.discharging[i] * self.turbine_flow_min,
                doc="Minimum turbine flow constraint",
            )
            # The total power required for the turbine
            self.add_constraint(
                "constraint_turbine_power_modulating",
                self.model.i,
                rule=lambda m, i: self.turbine_power[i]
                == self.number_of_turbines
                * self.BEP_turbine_power
                * (self.turbine_flow[i] / self.BEP_turbine_flow)
                + self.K_pipe_losses * self.turbine_flow[i],
                doc="Turbine modulating power",
            )

        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.pump_power[i] - self.turbine_power[i],
        )

        self.add_constraint(
            "constraint_link_charging_discharging",
            self.model.i,
            rule=lambda m, i: self.charging[i] + self.discharging[i] <= 1,
            doc="charging and discharging constraint",
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("charging")] = [
            pyomo.value(self.charging[i]) for i in self.model.i
        ]
        df[self.namespace("discharging")] = [
            pyomo.value(self.discharging[i]) for i in self.model.i
        ]
        df[self.namespace("pump_flow")] = [
            pyomo.value(self.pump_flow[i]) for i in self.model.i
        ]
        df[self.namespace("turbine_flow")] = [
            pyomo.value(self.turbine_flow[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("pump_power")] = [
            pyomo.value(self.pump_power[i]) for i in self.model.i
        ]
        df[self.namespace("turbine_power")] = [
            pyomo.value(self.turbine_power[i]) for i in self.model.i
        ]
        df[self.namespace("height")] = [
            pyomo.value(self.height[i]) for i in self.model.i
        ]
        df[self.namespace("height_upper_reservoir")] = [
            pyomo.value(self.height_upper_reservoir[i]) for i in self.model.i
        ]
        df[self.namespace("height_lower_reservoir")] = [
            pyomo.value(self.height_lower_reservoir[i]) for i in self.model.i
        ]
        df[self.namespace("SOC")] = [pyomo.value(self.SOC[i]) for i in self.model.i]

        return df


class TidalTurbine(ComponentModel):
    """
    Basic model for tidal turbine

    """

    def __init__(
        self,
        *args,
        dock_area=5000,
        min_dock_level=0.00,
        max_dock_level=50.00,
        min_delta=1.55,
        max_delta=4.00,
        number_turbines=1,
        min_flow=1.20,
        max_flow=3.00,
        eta_turbine=0.5,
        **kwargs,
    ):
        """
        delta h, Model A 1: min delta 1.55, max delta 4.00
        """
        super().__init__(*args, **kwargs)
        discret_turbine = 5

        self.turbine_index = range(discret_turbine)
        turbines_flows = np.zeros(discret_turbine)

        for i in range(discret_turbine):
            turbines_flows[i] = min_flow + i * (max_flow - min_flow) / (
                discret_turbine - 1
            )

        rho = 1e3
        gravity = 9.81

        # area and height
        self.dock_area = dock_area
        self.min_dock_level = min_dock_level
        self.max_dock_level = max_dock_level

        # turbine
        self.min_delta = min_delta
        self.max_delta = max_delta
        self.min_flow = min_flow
        self.max_flow = max_flow

        self.number_turbines = number_turbines

        self.flow_levels = turbines_flows

        self.K_turbine = rho * gravity * eta_turbine

        print("Tidal Turbine Characteristics")
        print(turbines_flows)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("dock_level")]

        self.add_parameter(
            "charging",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("charging"), np.zeros(len(data.index))
            )[i],
            domain=pyomo.NonNegativeReals,
            doc="Charing dock, (-)",
        )
        # Levels - flows
        self.add_parameter(
            "flow_levels_par",
            self.model.i,
            self.turbine_index,
            initialize=lambda m, i, j: self.flow_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Turbine water flow levels, (m3/s)",
        )
        self.add_parameter(
            "delta_level_max",
            self.model.i,
            initialize=lambda m, i: self.max_delta * np.ones(len(data.index))[i],
            doc="Maximum head turbine, (m)",
        )
        self.add_parameter(
            "delta_level_min",
            self.model.i,
            initialize=lambda m, i: self.min_delta * np.ones(len(data.index))[i],
            doc="Minimum head turbine, (m)",
        )
        self.add_parameter(
            "flow_max",
            self.model.i,
            initialize=lambda m, i: (self.number_turbines * self.max_flow)
            * np.ones(len(data.index))[i],
            doc="Maximum flow in turbine , (m3/s)",
        )
        self.add_parameter(
            "flow_min",
            self.model.i,
            initialize=lambda m, i: self.min_flow * np.ones(len(data.index))[i],
            doc="Minimum flow in turbine, (m3/s)",
        )
        # Initial height
        self.add_parameter(
            "dock_level_ini",
            initialize=lambda m: ini.get(self.namespace("dock_level")),
            doc="Initial height water, (m)",
        )
        self.add_variable(
            "turbine_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )
        # tidal info
        self.add_parameter(
            "zeeschelde_level",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("zeeschelde_level"), np.zeros(len(data.index))
            )[i],
            domain=pyomo.NonNegativeReals,
            doc="zeeschelde river height water, (m)",
        )
        self.add_parameter(
            "on_ini",
            initialize=lambda m: ini.get(self.namespace("on"), 0),
            doc="",
        )

        # variables
        self.add_variable(
            "flow_binary",
            self.model.i,
            self.turbine_index,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variables indicating turbine flow level: [1], [2], [3]",
        )
        self.add_variable(
            "power_add_vars",
            self.model.i,
            self.turbine_index,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Turbine power levels, (W)",
        )
        self.add_variable(
            "flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Turbine water flow, (m3/s)",
        )

        self.add_variable(
            "dock_level",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Water height in water tower, (m)",
        )
        self.add_variable(
            "delta_level",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Delta water height, (m)",
        )
        self.add_variable(
            "on",
            self.model.i,
            initialize=0,
            domain=pyomo.Binary,
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("start_up_cost"), np.zeros(len(data.index))
            )[i],
            doc="Time dependent start up cost (EUR)",
        )
        self.add_parameter(
            "running_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("running_cost"), np.zeros(len(data.index))
            )[i],
            doc="Running cost,  (EUR)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            initialize=0,
            domain=pyomo.Reals,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        # T U R B I N E S
        # discrete
        self.add_constraint(
            "constraint_flow_binary_and_discharging",
            self.model.i,
            rule=lambda m, i: self.on[i]
            == sum(self.flow_binary[i, j] for j in self.turbine_index),
            doc=(
                "Constraint of turbine flow binary variable, can be one on the"
                " selected flow levels, [1,2,3]"
            ),
        )
        self.add_constraint(
            "constraint_flow_rate",
            self.model.i,
            rule=lambda m, i: self.flow[i]
            == sum(
                self.flow_binary[i, j] * self.flow_levels_par[i, j]
                for j in self.turbine_index
            ),
            doc="water flow in pumps, [m3/s]",
        )

        # turbine power constraints
        self.add_constraint(
            "constraint_power_1",
            self.model.i,
            self.turbine_index,
            rule=lambda m, i, j: self.power_add_vars[i, j]
            <= self.flow_binary[i, j]
            * self.flow_levels_par[i, j]
            * self.K_turbine
            * self.delta_level_max[i],
            doc="1st constraint - turbine power the maximum possible pump power",
        )
        self.add_constraint(
            "constraint_power_2",
            self.model.i,
            self.turbine_index,
            rule=lambda m, i, j: self.power_add_vars[i, j]
            <= self.flow_levels_par[i, j] * self.K_turbine * self.delta_level[i],
            doc=(
                "2nd constraint - turbine power is less than product between"
                " flow and water height"
            ),
        )
        self.add_constraint(
            "constraint_power_3",
            self.model.i,
            self.turbine_index,
            rule=lambda m, i, j: self.power_add_vars[i, j]
            >= self.flow_levels_par[i, j] * self.K_turbine * self.delta_level[i]
            - (1 - self.flow_binary[i, j])
            * self.flow_levels_par[i, j]
            * self.K_turbine
            * self.delta_level_max[i],
            doc="3rd constraint - Additional complex constraint",
        )
        self.add_constraint(
            "constraint_power_4",
            self.model.i,
            self.turbine_index,
            rule=lambda m, i, j: self.power_add_vars[i, j] >= 0,
            doc="4th constraint - turbine power should be higher than 0",
        )

        # turbine power total
        self.add_constraint(
            "constraint_power_tot",
            self.model.i,
            rule=lambda m, i: self.turbine_power[i]
            == sum(self.power_add_vars[i, j] for j in self.turbine_index),
            doc="Total turbine power, (W)",
        )
        """
        # system constraints
        self.add_constraint(
            'dock_level_ini',
            rule=lambda m:
                self.dock_level[0] == self.dock_level_ini
        )
        """
        """
        self.add_constraint(
            'constraint_dock_level',
            self.model.i,
            rule=lambda m, i:
                self.dock_area * (self.dock_level[i+1] - self.dock_level[i])/(m.timestamp[i+1] - m.timestamp[i]) ==
                self.charging[i] * self.dock_area * (self.zeeschelde_level[i+1] - self.zeeschelde_level[i])/(m.timestamp[i+1] - m.timestamp[i]) - 
                (1 - self.charging[i]) * self.flow[i] if (i+1 < len(m.i)) #and self.charging == 0) 
                else  pyomo.Constraint.Skip #self.dock_level[i] == self.zeeschelde_level[i]
        )
        """
        self.add_constraint(
            "constraint_dock_level",
            self.model.i,
            rule=lambda m, i: (
                self.dock_level[i + 1]
                == (1 - self.charging[i])
                * (
                    self.dock_level[i]
                    - (m.timestamp[i + 1] - m.timestamp[i])
                    * self.flow[i]
                    / self.dock_area
                )
                + self.charging[i] * self.zeeschelde_level[i + 1]
                if (i + 1 < len(m.i))
                else pyomo.Constraint.Skip
            ),  # self.dock_level[i] == self.zeeschelde_level[i]
        )

        self.add_constraint(
            "constraint_delta_level",
            self.model.i,
            rule=lambda m, i: self.delta_level[i]
            == self.dock_level[i] - self.zeeschelde_level[i],
        )

        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i] == -self.turbine_power[i],
        )
        self.add_constraint(
            "constraint_delta_level_min",
            self.model.i,
            rule=lambda m, i: self.delta_level[i]
            >= self.delta_level_min[i] * self.on[i],
        )

        self.add_constraint(
            "constraint_turbine_on_charging",
            self.model.i,
            rule=lambda m, i: self.on[i] + self.charging[i] <= 1,
        )

        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            >= (
                self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
                if i - 1 > 0
                else self.start_up_cost[i] * (self.on[i] - self.on_ini)
            )
            + (
                self.on[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                * self.running_cost[i]
                / 3600
                if i + 1 < len(m.i)
                else 0
            ),
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("charging")] = [
            pyomo.value(self.charging[i]) for i in self.model.i
        ]
        df[self.namespace("dock_level")] = [
            pyomo.value(self.dock_level[i]) for i in self.model.i
        ]
        df[self.namespace("zeeschelde_level")] = [
            pyomo.value(self.zeeschelde_level[i]) for i in self.model.i
        ]
        df[self.namespace("delta_level")] = [
            pyomo.value(self.delta_level[i]) for i in self.model.i
        ]
        df[self.namespace("flow")] = [pyomo.value(self.flow[i]) for i in self.model.i]
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]

        return df


class WaterTowerModel(ComponentModel):
    """
    Basic model for water tower

    """

    def __init__(
        self,
        *args,
        radius=17.845,
        height_min=30,
        height_max=40,
        number_pumps=4,
        number_turbines=2,
        min_pump_flow=0.0278,
        max_pump_flow=0.3055,
        nominal_pump_power=155.1e3,
        nominal_pump_flow=0.287,
        max_pump_power=159.08e3,
        min_turbine_flow=0.246,
        max_turbine_flow=1.40,
        nominal_turbine_power=296.2e3,
        nominal_turbine_flow=1.40,
        max_turbine_power=296.2e3,
        eta_pump=0.801 * 0.959,
        eta_turbine=0.9,
        **kwargs,
    ):
        """
        Option 1: Q=2.78 m3/s and P=866 kWe
        Option 2: Q=2.00 m3/s and P=500 kWe
        Option 3: Q=0.246-1.4 m3/s and P=45-296.2 kWe
        radius: 17.845, 25.24, 30.91, 35.69, 39.90
        """
        super().__init__(*args, **kwargs)
        N_pumps = 4
        self.pump_index = range(N_pumps)
        self.turbine_index = range(number_turbines)
        pumps_flows = np.zeros(N_pumps)
        pumps_powers = np.zeros(N_pumps)
        turbines_flows = np.zeros(number_turbines)
        turbines_powers = np.zeros(number_turbines)

        min_pump_power = min_pump_flow * (nominal_pump_power / nominal_pump_flow)
        for i in range(N_pumps):
            pumps_flows[i] = min_pump_flow + (i + 1) * (max_pump_flow - min_pump_flow)
            pumps_powers[i] = min_pump_power + (i + 1) * (
                max_pump_power - min_pump_power
            )
        for i in range(number_turbines):
            turbines_flows[i] = (i + 1) * max_turbine_flow
            turbines_powers[i] = (i + 1) * max_turbine_power

        rho = 1e3
        gravity = 9.81

        # water tower geometry
        self.raduis = radius
        self.height_max = height_max
        self.height_min = height_min
        self.area = radius * radius * 3.14
        self.volume = self.area * (self.height_max - self.height_min)

        # pumps and turbines in water tower
        self.min_pump_flow = min_pump_flow
        self.max_pump_flow = max_pump_flow

        self.min_turbine_flow = min_turbine_flow
        self.max_turbine_flow = max_turbine_flow

        self.number_pumps = number_pumps
        self.number_turbines = number_turbines

        self.nominal_pump_flow = nominal_pump_flow
        self.nominal_pump_power = nominal_pump_power
        self.nominal_turbine_flow = nominal_turbine_flow
        self.nominal_turbine_power = nominal_turbine_power

        self.pump_flow_levels = pumps_flows
        self.turbine_flow_levels = turbines_flows

        self.pump_power_levels = pumps_powers
        self.turbine_power_levels = turbines_powers

        self.K_pump = rho * gravity * eta_pump
        self.eta_turbine = eta_turbine
        print("Pump and Turbines Characteristics")
        print(pumps_flows)
        print(pumps_powers)
        print(turbines_flows)
        print(turbines_powers)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("height")]

        # Levels - flows and powers
        self.add_parameter(
            "pump_flow_levels_par",
            self.model.i,
            self.pump_index,
            initialize=lambda m, i, j: self.pump_flow_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Pump water flow levels, (m3/s)",
        )
        self.add_parameter(
            "turbine_flow_levels_par",
            self.model.i,
            self.turbine_index,
            initialize=lambda m, i, j: self.turbine_flow_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Turbine water flow levels, (m3/s)",
        )
        self.add_parameter(
            "pump_power_levels_par",
            self.model.i,
            self.pump_index,
            initialize=lambda m, i, j: self.pump_power_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Pump power levels, (W)",
        )
        self.add_parameter(
            "turbine_power_levels_par",
            self.model.i,
            self.turbine_index,
            initialize=lambda m, i, j: self.turbine_power_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Turbine power levels, (W)",
        )
        # FLOW max/min
        self.add_parameter(
            "pump_flow_max",
            self.model.i,
            initialize=lambda m, i: (self.number_pumps * self.max_pump_flow)
            * np.ones(len(data.index))[i],
            doc="Maximum the total pump power, (W)",
        )
        self.add_parameter(
            "pump_flow_min",
            self.model.i,
            initialize=lambda m, i: self.min_pump_flow * np.ones(len(data.index))[i],
            doc="Minimum the total pump power, (W)",
        )

        self.add_parameter(
            "turbine_flow_max",
            self.model.i,
            initialize=lambda m, i: (self.number_turbines * self.max_turbine_flow)
            * np.ones(len(data.index))[i],
            doc="Maximum the total turbine power, (W)",
        )
        self.add_parameter(
            "turbine_flow_min",
            self.model.i,
            initialize=lambda m, i: self.min_turbine_flow * np.ones(len(data.index))[i],
            doc="Minimum the total turbine power, (W)",
        )

        self.add_parameter(
            "height_ini",
            initialize=lambda m: ini.get(self.namespace("height")),
            doc="Initial height water, (m)",
        )
        """
        self.add_parameter(
            'start_up_cost',
            self.model.i,
            initialize=lambda m, i: data.get(self.namespace('start_up_cost'), np.zeros(len(data.index)))[i],
            doc='Time dependent start up cost (W)'
        )
        """
        """
        self.add_parameter(
            'pump_flow_binary_ini',
            initialize=lambda m: ini.get(self.namespace('pump_flow_binary'), 0),
            doc='Time dependent start up cost (W)'
        )
        """
        # variables
        """
        self.add_variable(
            'pump_flow_binary',
            self.model.i, self.pump_index,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc='Binary variables indicating pump flow level: [1], [2], [3] and [4]'
        )
        """
        """
        self.add_variable(
            'turbine_flow_binary',
            self.model.i, self.turbine_index,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc='Binary variables indicating turbine flow level: [1], [2], [3]'
        )
        """
        """
        self.add_variable(
            'pump_power_add_vars',
            self.model.i, self.pump_index,
            domain=pyomo.NonNegativeReals,
            initialize=0.,
            doc='Pump power levels, (W)'
        )  
        self.add_variable(
            'turbine_power_add_vars',
            self.model.i, self.turbine_index,
            domain=pyomo.NonNegativeReals,
            initialize=0.,
            doc='Turbine power levels, (W)'
        )  
        """
        self.add_variable(
            "pump_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Pump water flow, (m3/s)",
        )
        self.add_variable(
            "turbine_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Turbine water flow, (m3/s)",
        )
        self.add_variable(
            "pump_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "turbine_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )
        self.add_variable(
            "height",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (self.height_min, self.height_max),
            initialize=0,
            doc="Water height in water tower, (m)",
        )
        self.add_variable(
            "SOC",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, 1),
            initialize=0,
            doc="State of charges, (-)",
        )
        self.add_variable(
            "charging",
            self.model.i,
            initialize=0,
            domain=pyomo.Binary,
        )
        self.add_variable(
            "discharging",
            self.model.i,
            initialize=0,
            domain=pyomo.Binary,
        )
        """
        self.add_variable(
            'operational_cost_pump',
            self.model.i, self.pump_index,
            domain=pyomo.Reals,
        )
        self.add_variable(
            'operational_cost',
            self.model.i,
            domain=pyomo.Reals,
        )
        """

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        # P U M P S

        # modulating
        self.add_constraint(
            "constraint_pump_flow_max_modulating",
            self.model.i,
            rule=lambda m, i: self.pump_flow[i]
            <= self.charging[i] * self.pump_flow_max[i],
            doc="Pump power, (W)",
        )
        self.add_constraint(
            "constraint_pump_flow_min_modulating",
            self.model.i,
            rule=lambda m, i: self.pump_flow[i]
            >= self.charging[i] * self.pump_flow_min[i],
            doc="Pump power, (W)",
        )
        self.add_constraint(
            "constraint_pump_power_modulating",
            self.model.i,
            rule=lambda m, i: self.pump_power[i]
            == self.nominal_pump_power * (self.pump_flow[i] / self.nominal_pump_flow),
            doc="water modulating flow, [m3/s]",
        )

        # T U R B I N E S
        # discrete
        """
        self.add_constraint(
            'constraint_turbine_flow_binary_and_discharging',
            self.model.i,
            rule=lambda m, i: self.discharging[i] == sum(self.turbine_flow_binary[i,j] for j in self.turbine_index),
            doc = 'Constraint of turbine flow binary variable, can be one on the selected flow levels, [1,2,3]'
        )
        self.add_constraint(
            'constraint_turbine_flow_rate',
            self.model.i,
            rule=lambda m, i: self.turbine_flow[i] == sum(self.turbine_flow_binary[i,
            j] * self.turbine_flow_levels_par[i,j] for j in self.turbine_index),
            doc = 'water flow in pumps, [m3/s]'
        )  
        """
        # modulating
        self.add_constraint(
            "constraint_turbine_flow_max_modulating",
            self.model.i,
            rule=lambda m, i: self.turbine_flow[i]
            <= self.discharging[i] * self.turbine_flow_max[i],
            doc="Maximum turbine flow constraint",
        )
        self.add_constraint(
            "constraint_turbine_flow_min_modulating",
            self.model.i,
            rule=lambda m, i: self.turbine_flow[i]
            >= self.discharging[i] * self.turbine_flow_min[i],
            doc="Minimum turbine flow constraint",
        )

        # turbine power constraints

        # turbine power total
        """
        self.add_constraint(
            'constraint_turbine_power_tot',
            self.model.i,
            rule=lambda m, i: self.turbine_power[i] == sum(self.turbine_flow_binary[i,
            j] * self.turbine_power_levels_par[i,j] for j in self.turbine_index),
            doc = 'Total turbine power, (W)'
        )  
        """
        self.add_constraint(
            "constraint_turbine_power_modulating",
            self.model.i,
            rule=lambda m, i: self.turbine_power[i]
            == self.nominal_turbine_power
            * (self.turbine_flow[i] / self.nominal_turbine_flow),
            doc="Turbine modulating power",
        )

        # system constraints
        self.add_constraint(
            "water_height_ini",
            rule=lambda m: self.height[0] == self.height_ini,
        )
        self.add_constraint(
            "constraint_height",
            self.model.i,
            rule=lambda m, i: (
                self.area
                * (self.height[i + 1] - self.height[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.pump_flow[i] - self.turbine_flow[i]
                if i + 1 < len(m.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_SOC",
            self.model.i,
            rule=lambda m, i: self.SOC[i]
            == self.area * (self.height[i] - self.height_min) / self.volume,
        )

        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.pump_power[i] - self.turbine_power[i],
        )

        self.add_constraint(
            "constraint_link_charging_discharging",
            self.model.i,
            rule=lambda m, i: self.charging[i] + self.discharging[i] <= 1,
            doc="charging and discharging constraint",
        )

        """
        self.add_constraint(
            'constraint_operational_cost_pump',
            self.model.i,self.pump_index,
            rule=lambda m, i,j:
                self.operational_cost_pump[i,j] >=
                (self.start_up_cost[i]*(self.pump_flow_binary[i,j] - self.pump_flow_binary[i-1,j]) if i-1 > 0 else
                 self.start_up_cost[i]*(self.pump_flow_binary[i,j] - self.pump_flow_binary_ini))
        )
        self.add_constraint(
            'constraint_operational_cost',
            self.model.i,
            rule=lambda m, i:
                self.operational_cost[i] >= sum(self.operational_cost_pump[i,j] for j in self.pump_index),
        )
        """

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("charging")] = [
            pyomo.value(self.charging[i]) for i in self.model.i
        ]
        df[self.namespace("discharging")] = [
            pyomo.value(self.discharging[i]) for i in self.model.i
        ]
        df[self.namespace("pump_flow")] = [
            pyomo.value(self.pump_flow[i]) for i in self.model.i
        ]
        df[self.namespace("turbine_flow")] = [
            pyomo.value(self.turbine_flow[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("pump_power")] = [
            pyomo.value(self.pump_power[i]) for i in self.model.i
        ]
        df[self.namespace("turbine_power")] = [
            pyomo.value(self.turbine_power[i]) for i in self.model.i
        ]
        df[self.namespace("height")] = [
            pyomo.value(self.height[i]) for i in self.model.i
        ]
        df[self.namespace("SOC")] = [pyomo.value(self.SOC[i]) for i in self.model.i]

        return df


class TurbulentTurbine(ComponentModel):
    def __init__(self, *args, BTF=0.2, OW=4, dock_area=5000, peakPower=200, **kwargs):
        super().__init__(*args, **kwargs)
        self.BTF = BTF
        self.OW = OW
        self.dock_area = dock_area
        self.peakPower = peakPower

        self.fCoeffs1 = [
            0.0,
            1.1790965951,
            0.8610676648,
            0.8487214532,
            1.4075702129,
            0.9912797275,
        ]
        self.fCoeffs2 = [
            0.0,
            -4.7276201572,
            7.0016736673,
            -5.0527748658,
            -2.1371707125,
            0.0367522672,
        ]

    def smoothmax(x, y, k=20):
        u = x  # /np.sqrt(x + y)
        v = y  # /np.sqrt(x + y)

        return u + v

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("dock_level")]
        # parameters
        self.add_parameter(
            "Big_Number",
            self.model.i,
            initialize=lambda m, i: 1e6 * np.ones(len(data.index))[i],
            domain=pyomo.NonNegativeReals,
            doc="Big number used for maximum function, (-)",
        )
        self.add_parameter(
            "elevOF",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("elevOF"), np.zeros(len(data.index))
            )[i],
            domain=pyomo.NonNegativeReals,
            doc="Elevation of outlet channel floor, (m)",
        )
        self.add_parameter(
            "elevTE",
            self.model.i,
            initialize=lambda m, i: self.elevOF[i] + 0.9,
            domain=pyomo.NonNegativeReals,
            doc="Elevation of turbine outlet, (m)",
        )
        self.add_parameter(
            "elevBF",
            self.model.i,
            initialize=lambda m, i: self.elevTE[i] + 0.61,
            domain=pyomo.NonNegativeReals,
            doc="Elevation of basin floor, (m)",
        )
        self.add_parameter(
            "zeeschelde_level",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("zeeschelde_level"), np.zeros(len(data.index))
            )[i],
            domain=pyomo.NonNegativeReals,
            doc="zeeschelde river height water, (m)",
        )
        self.add_parameter(
            "minimum_dock_level",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("minimum_dock_level"), np.zeros(len(data.index))
            )[i],
            domain=pyomo.NonNegativeReals,
            doc="minimum water level in dock during tides, (m)",
        )
        self.add_parameter(
            "maximum_water_flow",
            self.model.i,
            initialize=lambda m, i: 10.2 * np.ones(len(data.index))[i],
            domain=pyomo.NonNegativeReals,
            doc="Maximum water flow through turbine, (m3/s)",
        )
        # variables
        self.add_variable(
            "dock_level",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("dock_initial_level"), np.zeros(len(data.index))
            )[i],
            bounds=(0.0, 7.0),
            domain=pyomo.NonNegativeReals,
            doc="Dock initial level, (m)",
        )
        self.add_variable(
            "binary_level",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Binary variable that defines difference between zeeschelde and dock"
                " levels, (-)"
            ),
        )
        self.add_variable(
            "Max_level",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=5.0,
            doc="Maximum level between zeeshelde and dock, (-)",
        )
        self.add_variable(
            "Min_level",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=5.0,
            doc="Minimum level between zeeshelde and dock, (-)",
        )
        self.add_variable(
            "usl",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=(-0.5, 7.0),
            initialize=5.0,
            doc="Upstream level but measured from basin floor, (m)",
        )
        self.add_variable(
            "dsl",
            self.model.i,
            domain=pyomo.Reals,
            bounds=(-2.0, 7.0),
            initialize=2.0,
            doc="Downstream level but measured from basin floor, (m)",
        )
        self.add_variable(
            "sr",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=(0.0, 1.0),
            initialize=0.01,
            doc="Ratio between water levels, (-)",
        )
        self.add_variable(
            "effH",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.2,
            doc="Effective head difference, (m)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0.1,
            bounds=(0, self.peakPower),
            doc="Turbine power, (w)",
        )
        self.add_variable(
            "direction",
            self.model.i,
            bounds=(-1.0, 1.0),
            domain=pyomo.Reals,
            doc="water flow direction, (-)",
        )
        self.add_variable(
            "ingate",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=1.0,
            bounds=(0, 1),
            doc="Fraction of open gate, (-)",
        )
        self.add_variable(
            "inflow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.1,
            # bounds = (-10.2,10.2),
            doc="inflow through turbine, (m3/s)",
        )
        self.add_variable(
            "water_charging_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.1,
            doc="Water flow during charging, (m3/s)",
        )
        self.add_variable(
            "water_discharging_flow",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            initialize=-0.1,
            doc="Water flow during discharging, (m3/s)",
        )
        self.add_variable(
            "inQ",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.1,
            # bounds = (-10.2,10.2),
            doc="smooth inflow through turbine, (m3/s)",
        )
        self.add_variable(
            "QH",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.1,
            # bounds = (-10.2,10.2),
            doc="effective flow, (-)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_max_1",
            self.model.i,
            rule=lambda m, i: self.Max_level[i] >= self.zeeschelde_level[i],
            doc="Maximum level higher than zeescheele level",
        )
        self.add_constraint(
            "constraint_max_2",
            self.model.i,
            rule=lambda m, i: self.Max_level[i] >= self.dock_level[i],
            doc="Maximum level higher than dock level",
        )
        self.add_constraint(
            "constraint_max_3",
            self.model.i,
            rule=lambda m, i: self.Max_level[i]
            <= self.zeeschelde_level[i]
            + (1 - self.binary_level[i]) * self.Big_Number[i],
            doc="Maximum level less than zeeschelevel level and big number",
        )
        self.add_constraint(
            "constraint_max_4",
            self.model.i,
            rule=lambda m, i: self.Max_level[i]
            <= self.dock_level[i] + self.binary_level[i] * self.Big_Number[i],
            doc="Maximum level less than dock level and big number",
        )
        self.add_constraint(
            "constraint_min_1",
            self.model.i,
            rule=lambda m, i: self.Min_level[i] <= self.zeeschelde_level[i],
            doc="Minimum level higher than zeescheele level",
        )
        self.add_constraint(
            "constraint_min_2",
            self.model.i,
            rule=lambda m, i: self.Min_level[i] <= self.dock_level[i],
            doc="Minimum level than dock level",
        )
        self.add_constraint(
            "constraint_min_3",
            self.model.i,
            rule=lambda m, i: self.Min_level[i]
            >= self.zeeschelde_level[i] - self.binary_level[i] * self.Big_Number[i],
            doc="Minimum level higher than zeeschelevel level and big number",
        )
        self.add_constraint(
            "constraint_min_4",
            self.model.i,
            rule=lambda m, i: self.Min_level[i]
            >= self.dock_level[i] - (1 - self.binary_level[i]) * self.Big_Number[i],
            doc="Minimum level less than dock level and big number",
        )
        self.add_constraint(
            "constraint_upstream_level",
            self.model.i,
            rule=lambda m, i: self.usl[i] == self.Max_level[i] - self.elevBF[i],
            doc="Upstear level but measured from basin floor",
        )
        self.add_constraint(
            "constraint_downstream_level",
            self.model.i,
            rule=lambda m, i: self.dsl[i] == self.Min_level[i] - self.elevBF[i],
            doc="Upstear level but measured from basin floor",
        )
        self.add_constraint(
            "constraint_effective_water_level_difference",
            self.model.i,
            rule=lambda m, i: self.effH[i] == self.usl[i] - self.dsl[i],
            doc="Upstear level but measured from basin floor",
        )
        self.add_constraint(
            "constraint_direction",
            self.model.i,
            rule=lambda m, i: self.direction[i]
            == 1.0 * self.binary_level[i] + (-1.0) * (1 - self.binary_level[i]),
            doc="Direction of water flow",
        )
        self.add_constraint(
            "constraint_minimum_water_dock",
            self.model.i,
            rule=lambda m, i: self.dock_level[i] >= self.minimum_dock_level[i],
            doc="Minimum water level in dock",
        )
        self.add_constraint(
            "constraint_in_Q",
            self.model.i,
            rule=lambda m, i: self.inQ[i] == self.inflow[i],  # TODO
            doc="Minimum water level in dock",
        )
        self.add_constraint(
            "constraint_QH",
            self.model.i,
            rule=lambda m, i: self.QH[i] == self.inQ[i],  # *self.effH[i] TODO
            doc="Constraint QH",
        )
        self.add_constraint(
            "constraint_ratio_levels",
            self.model.i,
            rule=lambda m, i: self.sr[i]
            == (self.usl[i] + 0.61)
            / 1e3,  # TODO (self.dsl[i]+0.61)/(self.usl[i]+0.61),
            doc="Ratio levels",
        )
        self.add_constraint(
            "constraint_water_charging_flow",
            self.model.i,
            rule=lambda m, i: self.water_charging_flow[i]
            <= self.binary_level[i] * self.maximum_water_flow[i],
            doc="Water flow during charging less that the nominal water flow",
        )
        self.add_constraint(
            "constraint_water_discharging_flow",
            self.model.i,
            rule=lambda m, i: self.water_discharging_flow[i]
            >= -(1 - self.binary_level[i]) * self.maximum_water_flow[i],
            doc="Water flow during discharging less that the nominal water flow",
        )
        self.add_constraint(
            "constraint_inflow",
            self.model.i,
            rule=lambda m, i: self.inflow[i]
            == self.fCoeffs1[0]
            + self.fCoeffs1[2] * self.sr[i]
            + self.fCoeffs1[2] * self.effH[i],  # + self.fCoeffs1[3]*(self.sr[i]**2),
            # + self.fCoeffs1[4]*(self.sr[i]*self.effH[i]) + self.fCoeffs1[5]*(self.effH[i]**2)),
            doc="Constraint Inflow",
        )
        self.add_variable(
            "turbine_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == 0.9
            * (
                self.fCoeffs2[0]
                + self.fCoeffs2[1] * self.sr[i]
                + self.fCoeffs2[2] * self.QH[i]
            ),  # + self.fCoeffs2[3]*(self.sr[i]**2) \
            # + self.fCoeffs2[4]*(self.sr[i]*self.QH[i]) + self.fCoeffs2[5]*(self.QH[i]**2)),
        )
        self.add_constraint(
            "constraint_dock_level",
            self.model.i,
            rule=lambda m, i: (
                self.dock_level[i]
                == self.dock_level[i - 1]
                + (self.water_charging_flow[i - 1] + self.water_discharging_flow[i - 1])
                * (m.timestamp[i] - m.timestamp[i - 1])
                / self.dock_area
                if i > 0
                else pyomo.Constraint.Skip
            ),  # m.dock_level[i-1] + ,
            doc="Constraint dock level",
        )

    def get_results(self):
        df = pd.DataFrame()

        df[self.namespace("Max_level")] = [
            pyomo.value(self.Max_level[i]) for i in self.model.i
        ]
        df[self.namespace("Min_level")] = [
            pyomo.value(self.Min_level[i]) for i in self.model.i
        ]
        df[self.namespace("binary_level")] = [
            pyomo.value(self.binary_level[i]) for i in self.model.i
        ]
        df[self.namespace("direction")] = [
            pyomo.value(self.direction[i]) for i in self.model.i
        ]
        df[self.namespace("dock_level")] = [
            pyomo.value(self.dock_level[i]) for i in self.model.i
        ]
        df[self.namespace("zeeschelde_level")] = [
            pyomo.value(self.zeeschelde_level[i]) for i in self.model.i
        ]
        df[self.namespace("inflow")] = [
            pyomo.value(self.inflow[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]

        return df


component_models = {
    "PumpedStorageHydropower": PumpedStorageHydropower,
    "WaterTowerModel": WaterTowerModel,
    "TidalTurbine": TidalTurbine,
    "TurbulentTurbine": TurbulentTurbine,
}
