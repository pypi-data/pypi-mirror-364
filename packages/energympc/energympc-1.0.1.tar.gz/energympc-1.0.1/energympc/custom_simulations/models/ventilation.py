import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from .base import ComponentModel


class CentralVentilation(ComponentModel):
    """
    Central ventilation model with cycle recuperator
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "ventilation_rate",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("ventilation_rate"), np.zeros(len(data.index))
            )[i],
            doc="Ventilation rate (m3/s)",
        )
        self.add_parameter(
            "fresh_ratio",
            self.model.i,
            # bounds=lambda m, i: (0,1),
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(self.namespace("fresh_ratio_parameter"))[
                i
            ],
            doc="Air fresh ratio variable (-)",
        )
        """self.add_parameter(
            "fresh_ratio_parameter",
            self.model.i,
            initialize=lambda m, i: data.get(self.namespace("fresh_ratio_parameter"))[
                i
            ],
            doc="Air fresh ratio parameter (-)",
        )"""
        self.add_parameter(
            "recuperator_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("recuperator_efficiency"),
                np.ones(len(data.index)),
            )[i],
            doc="Recuperator efficiency of ventilation system -)",
        )
        self.add_parameter(
            "outdoor_temperature",
            self.model.i,
            domain=pyomo.Reals,
            initialize=lambda m, i: data[self.namespace("outdoor_temperature")][i],
            doc="Outdoor temperature that goes into central ventilation (°C)",
        )
        self.add_parameter(
            "temperature_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_violation_scale"),
                10 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the temperature constraint violation (EUR / kWh)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_max"), 500e3 * np.ones(len(data.index))
            )[i],
            doc="Heat exhanger capacity for heaitng (W)",
        )
        self.add_parameter(
            "cool_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("cool_max"), 500e3 * np.ones(len(data.index))
            )[i],
            doc="Heat exhanger capacity for cooling (W)",
        )
        self.add_parameter(
            "temperature_supply_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_supply_max"),
                25 * np.ones(len(data.index)),
            )[i],
            doc="Maximum supply temperature - soft (°C)",
        )
        self.add_parameter(
            "temperature_supply_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_supply_min"),
                20 * np.ones(len(data.index)),
            )[i],
            doc="Minimum supply temperature - soft (°C)",
        )
        self.add_parameter(
            "temperature_supply_max_hard",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_supply_max_hard"),
                25 * np.ones(len(data.index)),
            )[i],
            doc="Maximum supply temperature - hard (°C)",
        )
        self.add_parameter(
            "temperature_supply_min_hard",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_supply_min_hard"),
                10 * np.ones(len(data.index)),
            )[i],
            doc="Minimum supply temperature - hard (°C)",
        )
        self.add_variable(
            "temperature_min_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "temperature_max_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "temperature_supply",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.temperature_supply_min_hard[i],
                self.temperature_supply_max_hard[i],
            ),
            initialize=lambda m, i: data[self.namespace("temperature_supply")][i],
            doc="Requested supply temperature in ventilation system (°C)",
        )
        self.add_variable(
            "temperature_return",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Return temperature to ventilation system (°C)",
        )
        self.add_variable(
            "temperature_after_recuperator",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Temperature after recuperator and before heat exchangers (°C)",
        )
        self.add_variable(
            "temperature_mix",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Temperature after mixing - fresh and return air (°C)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_max[i]),
            initialize=0,
            doc=(
                "Heating or cooling of supplied air in central ventilation"
                " after recuperator (W)"
            ),
        )
        self.add_variable(
            "cool",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.cool_max[i], 0),
            initialize=0,
            doc=(
                "Heating or cooling of supplied air in central ventilation"
                " after recuperator (W)"
            ),
        )
        self.add_variable(
            "heat_supply",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (-self.cool_max[i], self.heat_max[i]),
            initialize=0,
            doc="Heat supply to the building (W)",
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        """
        self.add_constraint(
            'constraint_fresh_ratio',
            self.model.i,
            rule=lambda m, i:
                self.fresh_ratio[i] <= 1.0 #self.fresh_ratio_parameter[i] 
        )
        """
        self.add_constraint(
            "recuperator",
            self.model.i,
            rule=lambda m, i: self.temperature_after_recuperator[i]
            == self.outdoor_temperature[i]
            + self.recuperator_efficiency[i]
            * (self.temperature_return[i] - self.outdoor_temperature[i]),
        )
        self.add_constraint(
            "mixing",
            self.model.i,
            rule=lambda m, i: self.temperature_mix[i]
            == self.fresh_ratio[i] * self.temperature_after_recuperator[i]
            + (1 - self.fresh_ratio[i]) * self.temperature_return[i],
        )
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: self.heat[i] + self.cool[i]
            == 1.2
            * self.ventilation_rate[i]
            * (self.temperature_supply[i] - self.temperature_mix[i])
            * 1e3,
        )
        self.add_constraint(
            "constraint_temperature_min_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_min_slack[i]
            >= self.temperature_supply_min[i] - self.temperature_supply[i],
        )
        self.add_constraint(
            "constraint_temperature_max_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_max_slack[i]
            >= self.temperature_supply[i] - self.temperature_supply_max[i],
        )
        self.add_constraint(
            "constraint_heat_building_supply",
            self.model.i,
            rule=lambda m, i: self.heat_supply[i]
            == 1.2
            * self.ventilation_rate[i]
            * (self.temperature_supply[i] - self.temperature_return[i])
            * 1e3,
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (self.temperature_min_slack[i] + self.temperature_max_slack[i])
            / 3.6e6
            * self.temperature_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()

        df[self.namespace("ventilation_rate")] = [
            pyomo.value(self.ventilation_rate[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("heat_supply")] = [
            pyomo.value(self.heat_supply[i]) for i in self.model.i
        ]
        df[self.namespace("cool")] = [pyomo.value(self.cool[i]) for i in self.model.i]
        df[self.namespace("cool_max")] = [
            pyomo.value(self.cool_max[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_supply")] = [
            pyomo.value(self.temperature_supply[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_after_recuperator")] = [
            pyomo.value(self.temperature_after_recuperator[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_mix")] = [
            pyomo.value(self.temperature_mix[i]) for i in self.model.i
        ]
        df[self.namespace("fresh_ratio")] = [
            pyomo.value(self.fresh_ratio[i]) for i in self.model.i
        ]
        df[self.namespace("outdoor_temperature")] = [
            pyomo.value(self.outdoor_temperature[i]) for i in self.model.i
        ]

        return df


class VAVModel(ComponentModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_min"), np.zeros(len(data.index))
            )[i],
            doc="minimum temperature in VAV system (C)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_max"), np.zeros(len(data.index))
            )[i],
            doc="maximum temperature in VAV system (C)",
        )
        self.add_variable(
            "temperature_in",
            self.model.i,
            bounds=lambda m, i: (
                self.temperature_min[i],
                self.temperature_max[i],
            ),
            doc="Input temperature in VAV system (C)",
        )
        self.add_variable(
            "temperature_out",
            self.model.i,
            bounds=lambda m, i: (
                self.temperature_min[i],
                self.temperature_max[i],
            ),
            doc="Output temperature in VAV system (C)",
        )
        self.add_parameter(
            "ventilation_rate",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("ventilation_rate"), np.zeros(len(data.index))
            )[i],
            doc="Ventilation rate in VAV system, (m3/s)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_max"), 1000e3 * np.ones(len(data.index))
            )[i],
            doc="Heat exhanger capacity for heaitng (W)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            bounds=lambda m, i: (0, self.heat_max[i]),
            domain=pyomo.NonNegativeReals,
            doc="Heat in VAV system (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == self.ventilation_rate[i]
            * 1.2
            * (self.temperature_out[i] - self.temperature_in[i])
            * 1e3,
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("temperature_in")] = [
            pyomo.value(self.temperature_in[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_out")] = [
            pyomo.value(self.temperature_out[i]) for i in self.model.i
        ]

        return df


#
# _____________________________________________________________________________________________________________________
class GeneralVentilation(ComponentModel):
    """Common parameters, variables and constrains
    for ventilation system"""

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "minimum_on_time",
            initialize=par[self.namespace("minimum_on_time")],
            doc="Minimum time in the ON period, (h)",
        )
        self.add_parameter(
            "minimum_off_time",
            initialize=par[self.namespace("minimum_off_time")],
            doc="Minimum time in the OFF period, (h)",
        )
        self.add_parameter(
            "dt",
            initialize=par[self.namespace("dt")],
            doc="time step in calculation, (s)",
        )
        # Space - parameters
        self.add_parameter(
            "number_persons",
            initialize=par[self.namespace("number_persons")],
            doc="Number of persons in the conditioned space, (-)",
        )
        self.add_parameter(
            "volume",
            self.model.i,
            initialize=lambda m, i: data.get("{}.volume".format(self.name))[i],
            doc="Space volume, (m3)",
        )
        self.add_parameter(
            "area",
            self.model.i,
            initialize=lambda m, i: data.get("{}.area".format(self.name))[i],
            doc="Space area, (m2)",
        )
        # Indoor air properties - parameters
        self.add_parameter(
            "temperature_indoor",
            self.model.i,
            initialize=lambda m, i: data["{}.temperature_indoor".format(self.name)][i],
            doc="Dry-bulb indoor temperature in the conditioned space, (C)",
        )
        self.add_parameter(
            "relative_humidity_indoor",
            self.model.i,
            initialize=lambda m, i: data[
                "{}.relative_humidity_indoor".format(self.name)
            ][i],
            doc="Relative humidity of the conditioned space, (%)",
        )
        self.add_parameter(
            "humidity_indoor",
            self.model.i,
            initialize=lambda m, i: HAPropsSI(
                "W",
                "T",
                273.15 + self.temperature_indoor[i],
                "P",
                101325,
                "R",
                self.relative_humidity_indoor[i],
            ),
            doc="Absolute humidity of the conditioned space, (kg_water_vapour/kg_air)",
        )
        self.add_parameter(
            "enthalpy_indoor",
            self.model.i,
            initialize=lambda m, i: HAPropsSI(
                "H",
                "T",
                273.15 + self.temperature_indoor[i],
                "P",
                101325,
                "R",
                self.relative_humidity_indoor[i],
            ),
            doc="Enthalpy of indoor air, (J/kg)",
        )
        self.add_parameter(
            "spacific_volume_indoor",
            self.model.i,
            initialize=lambda m, i: HAPropsSI(
                "V",
                "T",
                273.15 + self.temperature_indoor[i],
                "P",
                101325,
                "R",
                self.relative_humidity_indoor[i],
            ),
            doc="Specific volume of indoor conditioned air, (m3/kg)",
        )
        # Outdoor air properties - parameters
        self.add_parameter(
            "temperature_outdoor",
            self.model.i,
            initialize=lambda m, i: data["{}.temperature_outdoor".format(self.name)][i],
            doc="Dry-bulb temperature of outdoor temperature, (C)",
        )
        self.add_parameter(
            "relative_humidity_outdoor",
            self.model.i,
            initialize=lambda m, i: data[
                "{}.relative_humidity_outdoor".format(self.name)
            ][i],
            doc="Relative humidity od outdoor air, (%)",
        )
        self.add_parameter(
            "humidity_outdoor",
            self.model.i,
            initialize=lambda m, i: HAPropsSI(
                "W",
                "T",
                273.15 + self.temperature_outdoor[i],
                "P",
                101325,
                "R",
                self.relative_humidity_indoor[i],
            ),
            doc="Absolute humidity of the outdoor air, (kg_water_vapour/kg_air)",
        )
        self.add_parameter(
            "enthalpy_outdoor",
            self.model.i,
            initialize=lambda m, i: HAPropsSI(
                "H",
                "T",
                273.15 + self.temperature_outdoor[i],
                "P",
                101325,
                "R",
                self.relative_humidity_outdoor[i],
            ),
            doc="Enthalpy of outdoor air, (J/kg)",
        )
        # General - parameter
        self.add_parameter(
            "on_ini",
            initialize=lambda m: ini.get(self.namespace("on"), 0),
            doc="ON/OFF system, (-)",
        )
        self.add_parameter("state_ini", initialize=0.90, doc="ON/OFF system, (-)")
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.start_up_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Start up cost of the ventilation system, (EUR)",
        )
        # Concentration CO2 parameters
        self.add_parameter(
            "CO2_concentration_fresh",
            initialize=350.0,
            doc="CO2 concentration in the fresh air, (ppm)",
        )
        self.add_parameter(
            "CO2_concentration_ini",
            initialize=ini.get(self.namespace("CO2_concentration"), 400.0),
            doc="Initial CO2 concentration in the space, (-)",
        )
        self.add_parameter(
            "humidity_generation",
            self.model.i,
            initialize=130
            * (
                HAPropsSI(
                    "W",
                    "T",
                    273.15 + self.temperature_indoor[0],
                    "P",
                    101325,
                    "R",
                    self.relative_humidity_indoor[0],
                )
                - HAPropsSI(
                    "W",
                    "T",
                    273.15 + 15,
                    "P",
                    101325,
                    "R",
                    self.relative_humidity_outdoor[0],
                )
            )
            / 3600,
            doc="Generation of water vapour in the conditioned space, (%/s)",
        )
        # Concentration CO2 parameters
        self.add_parameter(
            "CO2_concentration_fresh",
            initialize=350.0,
            doc="CO2 concentration in the fresh air, (ppm)",
        )
        self.add_parameter(
            "CO2_concentration_ini",
            initialize=ini.get(self.namespace("CO2_concentration"), 400.0),
            doc="Initial CO2 concentration in the space, (-)",
        )
        self.add_parameter(
            "CO2_generation",
            self.model.i,
            initialize=self.number_persons * 5.2e-06,
            doc=(
                "The estimation of CO2 generation, 5.2 e-03 l/s from"
                " literature, (m3CO2/s)"
            ),
        )
        self.add_parameter(
            "humidity_ini",
            initialize=self.humidity_indoor[0],
            doc="Initial humidity in the space, (-)",
        )

        # System - variables
        self.add_variable(
            "fan_consumption",
            self.model.i,
            initialize=0,
            domain=pyomo.NonNegativeReals,
            doc="Fan consumption in the recuperation system, (W)",
        )
        self.add_variable(
            "rate",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Ventilation air flow rate, (m3/s)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            initialize=0.0,
            domain=pyomo.Reals,
            doc="Ventilation heat, (W)",
        )
        self.add_variable(
            "electricity_load",
            self.model.i,
            initialize=0.0,
            domain=pyomo.Reals,
            doc="Electricity consumption influenced by ventilation, (W)",
        )
        # Concentration - variables
        self.add_variable(
            "CO2_concentration",
            self.model.i,
            bounds=(self.CO2_concentration_fresh, 1000.0),
            initialize=self.CO2_concentration_ini,
            doc=(
                "The CO2 concentration in the space: CO2(ASHRAE: CO2"
                " concentration limit 1000 ppm), (ppm)"
            ),
        )
        self.add_variable(
            "humidity",
            self.model.i,
            initialize=self.humidity_ini,
            doc="The absolute humidity in the space, (kg_water_vapour/kg_air)",
        )

        # General - variables

        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the ventilation system, (EUR)",
        )
        self.add_variable(
            "operational_state",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the ventilation system, (EUR)",
        )
        self.add_variable(
            "state",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=self.state_ini,
            bounds=(0, 3),
            doc="Variable state indication of vantilation",
        )
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=self.on_ini,
            bounds=(0, 1),
            doc=(
                "Binary variable indicating the ventilation sytem operation,"
                " [1] - on or [0] - off"
            ),
        )


#
# _____________________________________________________________________________________________________________________
class VentilationSystemModel(GeneralVentilation):
    """
    General ventilation System
    Ventilation flow range (Rate_min, Rate_max)
    CO2 concentration modeling
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "ACH",
            self.model.i,
            initialize=lambda m, i: data.get("{}.air_changes_hours".format(self.name))[
                i
            ],
            doc="Number of air changes per hour, (-)",
        )
        # Ventilation rate range
        self.add_parameter(
            "rate_max",
            self.model.i,
            initialize=lambda m, i: data.get("{}.rate_max".format(self.name))[i],
            doc="Maximum flow rate, (m3/s)",
        )
        self.add_parameter(
            "rate_min",
            self.model.i,
            initialize=lambda m, i: data.get("{}.rate_min".format(self.name))[i],
            doc="Minimum flow rate, (m3/s)",
        )
        # Efficiency
        self.add_parameter(
            "efficiency",
            initialize=0.50,
            doc="Efficiency of air recuperator, (-)",
        )

    def extend_model_constraints(self, data, par, ini):
        # constraints
        self.add_constraint(
            "constraint_fan_consumption",
            self.model.i,
            rule=lambda m, i: self.fan_consumption[i] == 600 * self.rate[i] / 3600,
            doc="Fan curve, Q-Pf, (m3/s)",
        )
        self.add_constraint(
            "constraint_maximum_rate",
            self.model.i,
            rule=lambda m, i: self.rate[i] <= self.on[i] * self.rate_max[i] / 3600,
            doc="Maximum ventilation rate, (m3/s)",
        )
        self.add_constraint(
            "constraint_minimum_rate",
            self.model.i,
            rule=lambda m, i: self.rate[i] >= self.on[i] * self.rate_min[i] / 3600,
            doc="Minimum ventilation rate, (m3/s)",
        )
        self.add_constraint(
            "constraint_CO2_concentration",
            self.model.i,
            rule=lambda m, i: (
                self.volume[i]
                * (self.CO2_concentration[i] - self.CO2_concentration[i - 1])
                / self.dt
                == -self.rate[i] * (700 - self.CO2_concentration_fresh)
                + 1e09 * self.CO2_generation[i] / self.volume[i]
                if i > 0
                else self.CO2_concentration[0] == self.CO2_concentration_ini
            ),
        )
        self.add_constraint(
            "constraint_ventilation_heat",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == self.rate[i]
            * (1 / self.spacific_volume_indoor[i])
            * self.efficiency
            * (self.enthalpy_indoor[i] - self.enthalpy_outdoor[i]),
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            >= (
                self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
                if i > 0
                else self.start_up_cost[i] * (self.on[i] - self.on_ini)
            ),
        )
        self.add_constraint(
            "constraint_electricity_load",
            self.model.i,
            rule=lambda m, i: self.heat[i] == self.electricity_load[i] * 3,
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("rate")] = [pyomo.value(self.rate[i]) for i in self.model.i]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("fan_consumption")] = [
            pyomo.value(self.fan_consumption[i]) for i in self.model.i
        ]
        df[self.namespace("enthalpy_indoor")] = [
            pyomo.value(self.enthalpy_indoor[i]) for i in self.model.i
        ]
        df[self.namespace("enthalpy_outdoor")] = [
            pyomo.value(self.enthalpy_outdoor[i]) for i in self.model.i
        ]
        df[self.namespace("CO2_concentration")] = [
            pyomo.value(self.CO2_concentration[i]) for i in self.model.i
        ]

        return df


#
# _____________________________________________________________________________________________________________________
class SpecificVentilationSystem(GeneralVentilation):
    """
    Ventilation System with Air Recuperator
    system: Mitshubishi Lossnay LGH-100 RX5-E
    Inputs: indoor and outdoor air temperature
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.system = technical_data()
        self.q_min = demand_ventilation()

        self.ven_index = range(0, len(self.system["fan_power"]))
        self.hex_by = range(0, 2)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        # Enthalpy supply - Parameters
        self.add_parameter(
            "enthalpy_supply_par",
            self.model.i,
            self.ven_index,
            initialize=lambda m, i, j: self.enthalpy_outdoor[i]
            + self.system["efficiency"][j]
            * (self.enthalpy_indoor[i] - self.enthalpy_outdoor[i]),
            doc="Enthalpy of supply air, (J/kg)",
        )
        # System - Parameters
        self.add_parameter(
            "rate_par",
            self.model.i,
            self.ven_index,
            initialize=lambda m, i, j: (self.system["ventilation_rate"][j] / 3600),
            domain=pyomo.NonNegativeReals,
            doc="Flow in air recuperator, (m3/s)",
        )
        self.add_parameter(
            "fan_consumption_par",
            self.model.i,
            self.ven_index,
            initialize=lambda m, i, j: self.system["fan_power"][j],
            domain=pyomo.NonNegativeReals,
            doc="Fan consumption in the ventilation system, (W)",
        )
        # Heat - Parameters
        self.add_parameter(
            "heat_hex_par",
            self.model.i,
            self.ven_index,
            initialize=lambda m, i, j: self.rate_par[i, j]
            * (1 / self.spacific_volume_indoor[i])
            * (self.enthalpy_indoor[i] - self.enthalpy_supply_par[i, j]),
            domain=pyomo.Reals,
            doc="Possible heat gains influenced by the ventilation system, (W)",
        )
        self.add_parameter(
            "heat_bypass_par",
            self.model.i,
            self.ven_index,
            initialize=lambda m, i, j: self.rate_par[i, j]
            * (1 / self.spacific_volume_indoor[i])
            * (self.enthalpy_indoor[i] - self.enthalpy_outdoor[i]),
            domain=pyomo.Reals,
            doc="Possible heat gains influenced the ventilation system, (W)",
        )
        # Variables
        self.add_variable(
            "sys_variable",
            self.model.i,
            self.ven_index,
            self.hex_by,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Binary variables indicating the heat exchanger mode and fan"
                " level. Fan level: [1], [2], [3] and [4], and operation type:"
                " [0]- heat exchanger and [1] - bypass"
            ),
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_sys_variable",
            self.model.i,
            self.ven_index,
            self.hex_by,
            rule=lambda m, i, j, k: sum(
                self.sys_variable[i, j, k] for j in self.ven_index for k in self.hex_by
            )
            <= 1,
            doc="Ventilation level [1,2,3,4] and hex/by [0,1]",
        )
        self.add_constraint(
            "constraint_fan_consumption",
            self.model.i,
            self.ven_index,
            rule=lambda m, i, j: self.fan_consumption[i]
            == sum(
                self.sys_variable[i, j, k] * self.fan_consumption_par[i, j]
                for j in self.ven_index
                for k in self.hex_by
            ),
            doc="Fun consumptions from the technical database",
        )
        self.add_constraint(
            "constraint_ventilation_rate",
            self.model.i,
            self.ven_index,
            self.hex_by,
            rule=lambda m, i, j, k: self.rate[i]
            == sum(
                self.sys_variable[i, j, k] * self.rate_par[i, j]
                for j in self.ven_index
                for k in self.hex_by
            ),
            doc="Ventilation rates is the specific technical database",
        )
        self.add_constraint(
            "constraint_ventilation_heat",
            self.model.i,
            self.ven_index,
            rule=lambda m, i, j: self.heat[i]
            == sum(
                self.sys_variable[i, j, 0] * self.heat_hex_par[i, j]
                + self.sys_variable[i, j, 1] * self.heat_bypass_par[i, j]
                for j in self.ven_index
            ),
            doc="Heat influenced by the ventilation through heat exchanger",
        )
        """self.add_constraint(
            'constraint_state_variable',
            self.model.i,
            rule=lambda m,i: self.volume[i] * (self.state[i]-self.state[i-1])/self.dt == self.rate[i] - self.q_min  if i > 0  else self.state[0] == self.state_ini,
            doc='Variation of the state variable'
        )"""
        self.add_constraint(
            "constraint_CO2_concentration",
            self.model.i,
            rule=lambda m, i: (
                self.volume[i]
                * (self.CO2_concentration[i] - self.CO2_concentration[i - 1])
                / self.dt
                == -self.rate[i] * (700 - self.CO2_concentration_fresh)
                + (750 - self.CO2_concentration_fresh) * 100 / 3600
                if i > 0
                else self.CO2_concentration[0] == self.CO2_concentration_ini
            ),
        )
        self.add_constraint(
            "constraint_humidity",
            self.model.i,
            rule=lambda m, i: (
                self.volume[i] * (self.humidity[i] - self.humidity[i - 1]) / self.dt
                == -self.rate[i] * (self.humidity_indoor[i] - self.humidity_outdoor[i])
                + self.humidity_generation[i]
                if i > 0
                else self.humidity[0] == self.humidity_ini
            ),
        )
        self.add_constraint(
            "constraint_on_off_ventilation",
            self.model.i,
            rule=lambda m, i: self.on[i]
            == sum(
                self.sys_variable[i, j, k] for j in self.ven_index for k in self.hex_by
            ),
            doc="Variation of the state variable",
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            >= (
                self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
                if i > 0
                else self.start_up_cost[i] * (self.on[i] - self.on_ini)
            ),
        )

        self.add_constraint(
            "constraint_electricity_load",
            self.model.i,
            rule=lambda m, i: self.heat[i] == self.electricity_load[i] * 3,
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("rate")] = [pyomo.value(self.rate[i]) for i in self.model.i]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("fan_consumption")] = [
            pyomo.value(self.fan_consumption[i]) for i in self.model.i
        ]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("bypass")] = [
            pyomo.value(self.heat_bypass_par[i, 2]) for i in self.model.i
        ]
        df[self.namespace("heat_exchanger")] = [
            pyomo.value(self.heat_hex_par[i, 2]) for i in self.model.i
        ]
        df[self.namespace("hex1")] = [
            pyomo.value(self.sys_variable[i, 0, 0]) for i in self.model.i
        ]
        df[self.namespace("hex2")] = [
            pyomo.value(self.sys_variable[i, 1, 0]) for i in self.model.i
        ]
        df[self.namespace("hex3")] = [
            pyomo.value(self.sys_variable[i, 2, 0]) for i in self.model.i
        ]
        df[self.namespace("hex4")] = [
            pyomo.value(self.sys_variable[i, 3, 0]) for i in self.model.i
        ]
        df[self.namespace("by1")] = [
            pyomo.value(self.sys_variable[i, 0, 1]) for i in self.model.i
        ]
        df[self.namespace("by2")] = [
            pyomo.value(self.sys_variable[i, 1, 1]) for i in self.model.i
        ]
        df[self.namespace("by3")] = [
            pyomo.value(self.sys_variable[i, 2, 1]) for i in self.model.i
        ]
        df[self.namespace("by4")] = [
            pyomo.value(self.sys_variable[i, 3, 1]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        df[self.namespace("humidity")] = [
            pyomo.value(self.humidity[i]) for i in self.model.i
        ]
        df[self.namespace("CO2_concentration")] = [
            pyomo.value(self.CO2_concentration[i]) for i in self.model.i
        ]

        return df


def technical_data():
    # _________
    # mitsubishi_database - Mitsubishi_Lossnay RX5

    System_df = pd.DataFrame()

    LGH15RX5 = {
        "ventilation_rate": [70, 110, 150, 150],
        "fan_power": [35, 59, 90, 110],
        "efficiency": [0.810, 0.775, 0.750, 0.750],
    }
    LGH35RX5 = {
        "ventilation_rate": [115, 210, 350, 350],
        "fan_power": [69, 116, 169, 212],
        "efficiency": [0.815, 0.765, 0.715, 0.715],
    }
    LGH65RX5 = {
        "ventilation_rate": [265, 520, 650, 650],
        "fan_power": [140, 265, 322, 380],
        "efficiency": [0.78, 0.705, 0.685, 0.685],
    }
    LGH100RX5 = {
        "ventilation_rate": [415, 755, 1000, 1000],
        "fan_power": [200, 380, 475, 535],
        "efficiency": [0.80, 0.74, 0.725, 0.725],
    }

    Renovent_Excellent_300 = {
        "ventilation_rate": [50, 100, 150, 225],
        "fan_power": [9.2, 15.2, 29.2, 66.2],
        "efficiency": [0.85, 0.85, 0.85, 0.85],
    }
    Renovent_Excellent_400 = {
        "ventilation_rate": [50, 100, 200, 300],
        "fan_power": [8.6, 15.0, 40.0, 98.0],
        "efficiency": [0.85, 0.85, 0.85, 0.85],
    }

    # {'ventilation_rate':[200,400,755,1000], 'fan_power':[200,380, 475, 535],'efficiency':[0.87,0.83,0.80,0.80]}

    system = Renovent_Excellent_400

    return system


def demand_ventilation():
    # Ventilation Standard
    # Technical handbook - Mitsubishi, example of United Kingdom
    # Offices
    # 1. Area method
    # 2. Air exchange method
    # 3. Occupancy method
    # 4. Heat removal method

    q_rec_p_s = 12e-03  # m3/s/person - recommended volume per person
    q_min_p_s = 8e-03  # m3/s/person - minimum volume per person
    q_min_a_s = 1.3e-03  # m3/s/m2     - minimum volume per area

    # Conditioned Space Parameters
    Area = 100  # Area of conditioned space
    # Number of people/persons
    N_people = 4

    # Minimum ventilation rate per area
    q_min = min(q_min_a_s * Area, q_min_p_s * N_people)
    return q_min


component_models = {
    "CentralVentilation": CentralVentilation,
    "VAVModel": VAVModel,
    "GeneralVentilation": GeneralVentilation,
    "VentilationSystemModel": VentilationSystemModel,
    "SpecificVentilationSystem": SpecificVentilationSystem,
}
