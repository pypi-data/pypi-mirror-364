import numpy as np
import pyomo.environ as pyomo

from .base import ComponentModel
from .heat_base import (
    OnOffComponentModelBase,
)


class GasBoilerModel(OnOffComponentModelBase):
    """
    Gas boiler model with constant efficiency.
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.efficiency".format(self.name),
                0.90 * np.ones(len(data.index)),
            )[i],
            doc="Efficiency of the boiler, (-)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data["{}.heat_max".format(self.name)][i],
            doc="Maximum heat of the boiler, (W)",
        )
        self.add_parameter(
            "heat_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.heat_min".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Minimum heat of the boiler, (W)",
        )
        self.add_parameter(
            "running_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.running_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Running cost,  (EUR)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.start_up_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Start up cost of the boiler, (EUR)",
        )
        self.add_parameter(
            "calorific_value",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.calorific_value".format(self.name),
                12.03 * np.ones(len(data.index)),
            )[i],
            doc="Gas calorific value of gas, (kWh/m3)",
        )
        self.model.del_component(self.model_namespace("on_ini"))
        self.add_parameter(
            "on_ini",
            initialize=ini.get("{}.on".format(self.name), 0),
            doc="Initialisation of the boiler, (-)",
        )
        # Variables
        self.add_variable(
            "gas_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Gas flow to the boiler, (m3/h)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0.0,
            doc="Heat flow from the boiler, (W)",
        )
        self.model.del_component(self.model_namespace("on"))
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variable indicating the boiler operation [1] or [0]. (-)",
        )
        self.add_variable(
            "off",
            self.model.i,
            domain=pyomo.Binary,
            initialize=1,
            bounds=(0, 1),
            doc="Binary variable indicating the boiler operation [1] or [0]. (-)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the boiler cost, (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_heat_max",
            self.model.i,
            rule=lambda m, i: -self.heat[i] <= self.heat_max[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_heat_min",
            self.model.i,
            rule=lambda m, i: -self.heat[i] >= self.heat_min[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: self.efficiency[i]
            * self.calorific_value[i]
            * 1000
            * self.gas_flow[i]
            == -self.heat[i],
        )
        self.add_constraint(
            "constraint_off",
            self.model.i,
            rule=lambda m, i: self.off[i] == 1 - self.on[i],
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
        results = super().get_results()
        results[self.namespace("heat")] = [
            -pyomo.value(self.heat[i]) for i in self.model.i
        ]
        results[self.namespace("heat_min")] = [
            pyomo.value(self.heat_min[i]) for i in self.model.i
        ]
        results[self.namespace("heat_max")] = [
            pyomo.value(self.heat_max[i]) for i in self.model.i
        ]
        results[self.namespace("gas_flow")] = [
            -pyomo.value(self.gas_flow[i]) for i in self.model.i
        ]
        results[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        results[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        return results


class GasBoilerTemperatureModel(ComponentModel):
    """
    Gas boiler model with efficiency dependent of return temperature
    two types of gas boilers
        - classic and
        - condensed
    Predefined parameters:
    - eta list
    - return temperature list

    Output variables:
        - x1 - boiler efficiency and
        - x2 - gas flow
    Separation variables:
    - y1 = (x1+x2)/2
    - y2 = (x1-x2)/2
    - x1 x x2 = y1**2 - y2**2 --> x1 x x2 = y_12 - y_22

    l_1 - 87.75, u_1 - 98.00
    l_2 - 0.0,  u_2 - h_max / calorific_value
    """

    def __init__(self, *args, type=None, eta_index=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type
        self.cw = 4180
        self.rho = 1000
        self.parameters = {
            "condensed": {
                "eta_list": [98.00, 97.50, 93.00, 90.00, 88.25, 87.75, 87.50, 87.50],
                "T_return_list": [20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
            },
            "y_1_list": [43, 44, 45, 47, 49, 51, 53, 55],
            "y_12_list": [1849, 1936, 2025, 2209, 2401, 2601, 2809, 3025],
            "y_2_list": [35, 37, 39, 41, 43, 45, 47, 49],
            "y_22_list": [1225, 1369, 1521, 1681, 1849, 2025, 2209, 2401],
        }
        # [98.00, 97.50, 93.00, 90.00, 88.25, 87.75, 87.50, 87.50],
        # for i in range(len(self.parameters['condensed']['eta_list']))  :
        #    self.parameters['condensed']['eta_list'][i]= 0.97 * self.parameters['condensed']['eta_list'][i]
        self.br_index = range(len(self.parameters["y_12_list"]) - 1)
        self.bool_index = [0, 1, 2]

    def temperatue_supply_definition_by_outdoor(
        self,
        supply_temperature_array,
        outdoor_temperature_array,
        outdoor_temperature_current,
    ):
        if outdoor_temperature_current < outdoor_temperature_array[0]:
            return supply_temperature_array[0]
        elif (
            outdoor_temperature_current
            > outdoor_temperature_array[outdoor_temperature_array.__len__() - 1]
        ):
            return supply_temperature_array[outdoor_temperature_array.__len__() - 1]
        for i in range(1, len(outdoor_temperature_array)):
            if (
                outdoor_temperature_current >= outdoor_temperature_array[i - 1]
                and outdoor_temperature_current <= outdoor_temperature_array[i]
            ):
                x1 = outdoor_temperature_array[i - 1]
                x2 = outdoor_temperature_array[i]
                y1 = supply_temperature_array[i - 1]
                y2 = supply_temperature_array[i]
                return ((y2 - y1) / (x2 - x1)) * (outdoor_temperature_current - x1) + y1

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data["{}.heat_max".format(self.name)][i],
            doc="Maximum heat of the boiler, (W)",
        )
        self.add_parameter(
            "heat_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.heat_min".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Minimum heat of the boiler, (W)",
        )
        self.add_parameter(
            "calorific_value",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.calorific_value".format(self.name), 12.03 * np.ones(len(data.index))
            )[i],
            doc="Gas calorific value of gas, (kWh/m3)",
        )
        self.add_parameter(
            "mass_flow",
            self.model.i,
            domain=pyomo.Reals,
            initialize=lambda m, i: data.get(
                "{}.mass_flow".format(self.name), np.ones(len(data.index))
            )[i],
            doc="Water mass flow in boiler, (kg/s)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.start_up_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Start up cost of the boiler, (EUR)",
        )
        self.add_parameter(
            "running_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.running_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Running cost,  (EUR)",
        )
        self.add_parameter(
            "outdoor_temperature",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.outdoor_temperature".format(self.name),
                10 * np.ones(len(data.index)),
            )[i],
            doc="Outdoor temperature, C",
        )

        # Variables
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variable indicating the boiler operation [1] or [0]. (-)",
        )
        self.add_variable(
            "efficiency",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=98.0,
            bounds=(
                self.parameters[self.type]["eta_list"][-1],
                self.parameters[self.type]["eta_list"][0],
            ),
            doc="Efficiency of the boiler, (-)",
        )
        self.add_variable(
            "gas_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_max[i] / (self.calorific_value[i] * 1e3)),
            initialize=0.0,
            doc="Gas flow to the boiler, (m3/h)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0.0,
            doc="Heat flow from the boiler, (W)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the boiler cost, (EUR)",
        )
        self.add_variable(
            "temperature_return",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=(
                self.parameters[self.type]["T_return_list"][0],
                self.parameters[self.type]["T_return_list"][-1],
            ),
            initialize=80,
            doc="Water return temperature to the boiler, (C)",
        )
        self.add_variable(
            "temperature_supply",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=90,
            bounds=(self.parameters[self.type]["T_return_list"][0], 100),
            doc="Water supply temperature from the boiler, (C)",
        )
        self.add_variable(
            "SOS_bool",
            self.model.i,
            self.br_index,
            self.bool_index,
            domain=pyomo.Boolean,
            initialize=0,
            bounds=(0, 1),
            doc="Boolean variables for eta-temperature, y1-y2**2 and y2-y2**2",
        )
        self.add_variable(
            "SOS_real",
            self.model.i,
            self.br_index,
            self.bool_index,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            bounds=(0, 1),
            doc="Real variable for eta-temperature, y_1-y_22 and y_2-y_22",
        )
        self.add_variable(
            "y_1",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            bounds=(self.parameters["y_1_list"][0], self.parameters["y_1_list"][-1]),
            doc="separation variable - y_1",
        )
        self.add_variable(
            "y_2",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            bounds=(self.parameters["y_2_list"][0], self.parameters["y_2_list"][-1]),
            doc="separation variable - y_2",
        )
        self.add_variable(
            "y_12",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=self.parameters["y_12_list"][0],
            bounds=(self.parameters["y_12_list"][0], self.parameters["y_12_list"][-1]),
            doc="separation variable - y_12",
        )
        self.add_variable(
            "y_22",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=self.parameters["y_22_list"][0],
            bounds=(self.parameters["y_22_list"][0], self.parameters["y_22_list"][-1]),
            doc="separation variable - y_22",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_heat_max",
            self.model.i,
            rule=lambda m, i: -self.heat[i] <= self.heat_max[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_heat_min",
            self.model.i,
            rule=lambda m, i: -self.heat[i] >= self.heat_min[i] * self.on[i],
        )

        self.add_constraint(
            "constraint_eta_determination",
            self.model.i,
            rule=lambda m, i: self.efficiency[i]
            == sum(
                self.parameters[self.type]["eta_list"][j] * self.SOS_bool[i, j, 0]
                + (
                    self.parameters[self.type]["eta_list"][j + 1]
                    - self.parameters[self.type]["eta_list"][j]
                )
                * self.SOS_real[i, j, 0]
                for j in self.br_index
            ),
        )
        self.add_constraint(
            "constraint_temperature_return_SOS",
            self.model.i,
            rule=lambda m, i: self.temperature_return[i]
            == sum(
                self.parameters[self.type]["T_return_list"][j] * self.SOS_bool[i, j, 0]
                + (
                    self.parameters[self.type]["T_return_list"][j + 1]
                    - self.parameters[self.type]["T_return_list"][j]
                )
                * self.SOS_real[i, j, 0]
                for j in self.br_index
            ),
        )
        self.add_constraint(
            "constraint_y1_determination",
            self.model.i,
            rule=lambda m, i: self.y_1[i]
            == sum(
                self.parameters["y_1_list"][j] * self.SOS_bool[i, j, 1]
                + (self.parameters["y_1_list"][j + 1] - self.parameters["y_1_list"][j])
                * self.SOS_real[i, j, 1]
                for j in self.br_index
            ),
        ),
        self.add_constraint(
            "constraint_y12_determination",
            self.model.i,
            rule=lambda m, i: self.y_12[i]
            == sum(
                self.parameters["y_12_list"][j] * self.SOS_bool[i, j, 1]
                + (
                    self.parameters["y_12_list"][j + 1]
                    - self.parameters["y_12_list"][j]
                )
                * self.SOS_real[i, j, 1]
                for j in self.br_index
            ),
        ),
        self.add_constraint(
            "constraint_y2_determination",
            self.model.i,
            rule=lambda m, i: self.y_2[i]
            == sum(
                self.parameters["y_2_list"][j] * self.SOS_bool[i, j, 2]
                + (self.parameters["y_2_list"][j + 1] - self.parameters["y_2_list"][j])
                * self.SOS_real[i, j, 2]
                for j in self.br_index
            ),
        ),
        self.add_constraint(
            "constraint_y22_determination",
            self.model.i,
            rule=lambda m, i: self.y_22[i]
            == sum(
                self.parameters["y_22_list"][j] * self.SOS_bool[i, j, 2]
                + (
                    self.parameters["y_22_list"][j + 1]
                    - self.parameters["y_22_list"][j]
                )
                * self.SOS_real[i, j, 2]
                for j in self.br_index
            ),
        ),
        self.add_constraint(
            "constraint_efficiency",
            self.model.i,
            rule=lambda m, i: self.efficiency[i] == self.y_1[i] + self.y_2[i],
        )
        self.add_constraint(
            "constraint_gas_flow",
            self.model.i,
            rule=lambda m, i: self.gas_flow[i] == self.y_1[i] - self.y_2[i],
        )
        self.add_constraint(
            "constraint_heat_spec",
            self.model.i,
            rule=lambda m, i: (
                -self.heat[i] / (1e3 * self.calorific_value[i])
                == (self.y_12[i] - self.y_22[i]) / 1e2
                if i < len(m.i)
                else self.heat[i] == 0
            ),
        )

        for k in self.bool_index:
            for j in self.br_index:
                self.add_constraint(
                    "constraint_SOS_real_boolean_{}_{}".format(j, k),
                    self.model.i,
                    rule=lambda m, i: self.SOS_real[i, j, k] <= self.SOS_bool[i, j, k],
                )
                self.add_constraint(
                    "constraint_SOS_boolean_{}_{}".format(j, k),
                    self.model.i,
                    rule=lambda m, i: sum(self.SOS_bool[i, j, k] for j in self.br_index)
                    == 1,
                )
        self.add_constraint(
            "constraint_heat_temperature",
            self.model.i,
            rule=lambda m, i: -self.heat[i]
            == self.mass_flow[i]
            * self.cw
            * (self.temperature_supply[i] - self.temperature_return[i]),
        )
        self.add_constraint(
            "constraint_temperature_supply",
            self.model.i,
            rule=lambda m, i: self.temperature_supply[i]
            == self.temperatue_supply_definition_by_outdoor(
                [90, 82, 65, 20], [-10, 0, 10, 20], self.outdoor_temperature[i]
            ),
        )

        self.add_constraint(
            "constraint_heat_derivative_1",
            self.model.i,
            rule=lambda m, i: (
                self.heat[i + 1] - self.heat[i] <= self.heat_max[i] / 5
                if i + 1 < len(m.i)
                else self.heat[i] == 0
            ),
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        results[self.namespace("gas_flow")] = [
            pyomo.value(self.gas_flow[i]) for i in self.model.i
        ]
        results[self.namespace("heat")] = [
            -pyomo.value(self.heat[i]) for i in self.model.i
        ]
        results[self.namespace("efficiency")] = [
            pyomo.value(self.efficiency[i]) for i in self.model.i
        ]
        results[self.namespace("temperature_supply")] = [
            pyomo.value(self.temperature_supply[i]) for i in self.model.i
        ]
        results[self.namespace("temperature_return")] = [
            pyomo.value(self.temperature_return[i]) for i in self.model.i
        ]

        return results


class ElectricalHeaterModel(ComponentModel):
    """
    Electrical boiler model with constant efficiency

    """

    def extend_model_variables(self, data, par, ini):
        # Parameters
        self.add_parameter(
            "efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.efficiency".format(self.name),
                1.00 * np.ones(len(data.index)),
            )[i],
            doc="Efficiency of the boiler, (-)",
        )
        self.add_parameter(
            "power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.power_max".format(self.name),
                5000 * np.ones(len(data.index)),
            )[i],
            doc="Nominal power of the electrical boiler, (W)",
        )
        self.add_parameter(
            "running_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.running_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Running cost, (EUR)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.start_up_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Start up cost of the boiler, (EUR)",
        )

        self.add_parameter(
            "on_ini",
            initialize=ini.get("{}.on_ini".format(self.name), 0),
            doc="Initialisation of the boiler, (-)",
        )
        # Variables
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.power_max[i]),
            initialize=0.0,
            doc="Electrical power to the electrical boiler, (W)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.efficiency[i] * self.power_max[i], 0),
            initialize=0.0,
            doc="Heat flow from the electrical boiler, (W)",
        )
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variable indicating the boiler operation [1] or [0]. (-)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the electrical boiler cost, (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i] <= self.power_max[i],
            # rule=lambda m, i: self.power[i]  == self.on[i] * self.power_max[i]
        )
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: -self.heat[i] == self.efficiency[i] * self.power[i],
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
        df[self.namespace("heat")] = [-pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        return df


class RadiatorModel(ComponentModel):
    """
    Simple radiator model
    values:
    parameters: cw = 4186 (W/m2K), UA (values from table)
    variables : T_sup (supply temperature), T_ret (return temperature), T_in (indoor
    temperature), heat (heat delivered by radiator)
    heat = m x cw x (T_sup - T_ret)
    heat = UA x ((T_sup+T_ret)/2 - T_in)
    """

    # cw = 4186
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "UA",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.UA".format(self.name), 100 * np.ones(len(data.index))
            )[i],
            doc="Heat characteristic of the Radiator, (W/C)",
        )
        self.add_parameter(
            "cw",
            initialize=lambda m: par.get("cw", 4186),
            doc="Specific heat capacity, (J/kg*K)",
        )
        self.add_parameter(
            "mass_flow",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.mass_flow".format(self.name), 1 * np.ones(len(data.index))
            )[i],
            doc="Water mass flow through the radiator, (kg/s)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.heat_max".format(self.name),
                1000000 * np.ones(len(data.index)),
            )[i],
            doc="Maximum heat from the radiator, (W)",
        )
        # Variables
        self.add_variable(
            "heat_water",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_max[i]),
            initialize=0.0,
            doc="Heat through the Radiator, (W)",
        )
        self.add_variable(
            "heat_air",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0.0,
            doc="Heat through the Radiator, (W)",
        )
        self.add_variable(
            "temperature_supply",
            self.model.i,
            domain=pyomo.Reals,
            initialize=20,
            bounds=(0, 100),
            doc="Water supply temperature in the Radiator. (C)",
        )
        self.add_variable(
            "temperature_return",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=(0, 100),
            doc="Water return temperature from the Radiator. (C)",
        )
        self.add_variable(
            "temperature_indoor",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=(-100, 100),
            doc="Indoor air temperature in the zone of the Radiatorr. (C)",
        )
        self.add_variable(
            "temp_supp_req",
            self.model.i,
            domain=pyomo.Reals,
            initialize=20,
            bounds=(0, 100),
            doc="Supply requirements temperature in the zone of the Radiator. (C)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_water_heat",
            self.model.i,
            rule=lambda m, i: self.heat_water[i]
            == self.mass_flow[i]
            * (self.temperature_supply[i] - self.temperature_return[i])
            * self.cw,
        )
        # self.add_constraint(
        #     "constraint_air_heat",
        #     self.model.i,
        #     rule=lambda m, i: self.heat_air[i] == - self.UA[i] * ((self.temperature_supply[i] + self.temperature_return[i])/2 - self.temperature_indoor[i]),
        # )
        self.add_constraint(
            "constraint_air_water_heat",
            self.model.i,
            rule=lambda m, i: self.heat_water[i] == -self.heat_air[i],
        )
        self.add_constraint(
            "Temp supply req constraint",
            self.model.i,
            # rule=lambda m, i: self.heat_water[i] == - self.heat_air[i],
            rule=lambda m, i: -self.heat_air[i]
            == self.UA[i]
            * (
                (
                    self.temp_supp_req[i]
                    - (self.temperature_supply[i] - self.temperature_return[i]) / 2
                )
                - self.temperature_indoor[i]
            ),
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("heat_water")] = [
            pyomo.value(self.heat_water[i]) for i in self.model.i
        ]
        results[self.namespace("heat_air")] = [
            pyomo.value(self.heat_air[i]) for i in self.model.i
        ]
        results[self.namespace("temperature_supply")] = [
            pyomo.value(self.temperature_supply[i]) for i in self.model.i
        ]
        results[self.namespace("temperature_return")] = [
            pyomo.value(self.temperature_return[i]) for i in self.model.i
        ]
        results[self.namespace("temperature_indoor")] = [
            pyomo.value(self.temperature_indoor[i]) for i in self.model.i
        ]
        results[self.namespace("temp_supp_req")] = [
            pyomo.value(self.temp_supp_req[i]) for i in self.model.i
        ]
        return results


class GasBoilerTemperatureModel(GasBoilerModel):
    """
    Gas boiler model with constant efficiency.
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "mass_flow",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.mass_flow".format(self.name), 1 * np.ones(len(data.index))
            )[i],
            doc=(
                "Water flow through the boiler, (kg/s) ((Sum of mass flows of"
                " each zone))"
            ),
        )
        self.add_parameter(
            "cw",
            initialize=lambda m: par.get("cw", 4186),
            doc="Specific heat capacity, (J/kg*K)",
        )
        self.add_parameter(
            "outdoor_temperature",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.outdoor_temperature".format(self.name),
                10 * np.ones(len(data.index)),
            )[i],
            doc=(
                "OutDoor Temperature of the Zone (C) ((Should be connected"
                " with zone outdoor temperature))"
            ),
        )
        self.add_parameter(
            "temperature_losses",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_losses".format(self.name),
                5 * np.ones(len(data.index)),
            )[i],
            doc="Temperature_losses during heating process (C)",
        )
        self.add_parameter(
            "compensation_curve",
            initialize=par.get("{}.compensation_curve".format(self.name), False),
            doc=(
                "Is the supply temperature calculated with compensation curve"
                " equation or not, (Boolean)"
            ),
        )
        self.add_parameter(
            "compensation_curve_distribution_outdoor",
            range(len(par.get(f"{self.name}.compensation_curve_distribution_outdoor"))),
            initialize=lambda m, j: par.get(
                f"{self.name}.compensation_curve_distribution_outdoor", []
            )[j],
            doc="List of outdoor temperatures distribution ([])",
            within=pyomo.Any,
        )
        self.add_parameter(
            "compensation_curve_distribution_supply",
            range(len(par.get(f"{self.name}.compensation_curve_distribution_supply"))),
            initialize=lambda m, j: par.get(
                f"{self.name}.compensation_curve_distribution_supply", []
            )[j],
            doc="List of supply temperatures distribution ([])",
            within=pyomo.Any,
        )
        self.add_variable(
            "temperature_supply",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=(-100, 95),
            doc="Water supply temperature from the boiler, (C)",
        )
        self.add_variable(
            "temperature_supply_outdoor",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=(-100, 95),
            doc="Water supply temperature from the boiler, (C)",
        )
        self.add_variable(
            "temperature_requested_supply_max",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=(-100, 95),
            doc="",
        )
        self.add_variable(
            "temperature_return",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=(-100, 95),
            doc="Water return temperature to the boiler, (C)",
        )

    def temperatue_supply_definition_by_outdoor(
        self,
        supply_temperature_array,
        outdoor_temperature_array,
        outdoor_temperature_current,
    ):
        if outdoor_temperature_current < outdoor_temperature_array[0]:
            return supply_temperature_array[0]
        elif (
            outdoor_temperature_current
            > outdoor_temperature_array[outdoor_temperature_array.__len__() - 1]
        ):
            return supply_temperature_array[outdoor_temperature_array.__len__() - 1]
        for i in range(1, len(outdoor_temperature_array)):
            if (
                outdoor_temperature_current >= outdoor_temperature_array[i - 1]
                and outdoor_temperature_current <= outdoor_temperature_array[i]
            ):
                x1 = outdoor_temperature_array[i - 1]
                x2 = outdoor_temperature_array[i]
                y1 = supply_temperature_array[i - 1]
                y2 = supply_temperature_array[i]
                return ((y2 - y1) / (x2 - x1)) * (outdoor_temperature_current - x1) + y1

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_heat_max_2",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == -self.mass_flow[i]
            * (self.temperature_supply[i] - self.temperature_return[i])
            * self.cw,
        )
        self.add_constraint(
            "constraint_temperature_supply_outdoor",
            self.model.i,
            rule=lambda m, i: (
                self.temperature_supply_outdoor[i]
                == self.temperatue_supply_definition_by_outdoor(
                    self.compensation_curve_distribution_supply,
                    self.compensation_curve_distribution_outdoor,
                    self.outdoor_temperature[i],
                )
                if self.compensation_curve
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_temperature_requested_supply_max",
            self.model.i,
            rule=lambda m, i: self.temperature_supply[i]
            == self.temperature_requested_supply_max[i] + self.temperature_losses[i],
        )
        # rule = lambda m, i: self.operational_cost[i]
        # >= (
        #     self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
        #     if i - 1 > 0
        #     else self.start_up_cost[i] * (self.on[i] - self.on_ini)
        # )
        # + (
        #     self.on[i]
        #     * (m.timestamp[i + 1] - m.timestamp[i])
        #     * self.running_cost[i]
        #     / 3600
        #     if i + 1 < len(m.i)
        #     else 0
        # ),

    def get_results(self):
        results = super().get_results()
        results[self.namespace("heat")] = [
            -pyomo.value(self.heat[i]) for i in self.model.i
        ]
        results[self.namespace("heat_min")] = [
            pyomo.value(self.heat_min[i]) for i in self.model.i
        ]
        results[self.namespace("heat_max")] = [
            pyomo.value(self.heat_max[i]) for i in self.model.i
        ]
        results[self.namespace("gas_flow")] = [
            -pyomo.value(self.gas_flow[i]) for i in self.model.i
        ]
        results[self.namespace("temperature_supply")] = [
            pyomo.value(self.temperature_supply[i]) for i in self.model.i
        ]
        results[self.namespace("temperature_return")] = [
            pyomo.value(self.temperature_return[i]) for i in self.model.i
        ]
        results[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        results[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        results[self.namespace("temperature_supply_outdoor")] = [
            pyomo.value(self.temperature_supply_outdoor[i]) for i in self.model.i
        ]
        return results


component_models = {
    "GasBoilerModel": GasBoilerModel,
    "GasBoilerTemperatureModel": GasBoilerTemperatureModel,
    "RadiatorModel": RadiatorModel,
}
