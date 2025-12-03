import numpy as np
from abc import ABC, abstractmethod
import plotly.graph_objs as go
from dash import dash_table
import pandas as pd

from apex.core.lib.utils import round_format, round_2d_format

TABLE_WIDTH = '50%'
TABLE_MIN_WIDTH = '95%'


def random_color():
    r = np.random.randint(50, 200)
    g = np.random.randint(50, 200)
    b = np.random.randint(50, 200)
    return f'rgb({r}, {g}, {b})'


class PropertyReport(ABC):
    @staticmethod
    @abstractmethod
    def plotly_graph(res_data: dict, name: str):
        """
        Plot plotly graph.

        Parameters
        ----------
        res_data : dict
            The dict storing the result of the props
        Returns:
        -------
        list[plotly.graph_objs]
            The list of plotly graph object
        plotly.graph_objs.layout
            the layout
        """
        pass

    @staticmethod
    @abstractmethod
    def dash_table(res_data: dict, decimal: int) -> [dash_table.DataTable, pd.DataFrame]:
        """
        Make Dash table.

        Parameters
        ----------
        res_data : dict
            The dict storing the result of the props
        Returns:
        -------
        dash_table.DataTable
            The dash table object
        pd.DataFrame
        """
        pass


class EOSReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        vpa = []
        epa = []
        for k, v in res_data.items():
            vpa.append(k)
            epa.append(v)
        df = pd.DataFrame({
            "VpA(A^3)": vpa,
            "EpA(eV)": epa
        })
        trace = go.Scatter(
            name=name,
            x=df['VpA(A^3)'],
            y=df['EpA(eV)'],
            mode='lines+markers'
        )
        layout = go.Layout(
            title='Energy of State',
            xaxis=dict(
                title_text="VpA (A<sup>3</sup>)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            ),
            yaxis=dict(
                title_text="EpA (eV)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            )
        )

        return [trace], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        vpa = []
        epa = []
        for k, v in res_data.items():
            vpa.append(float(k))
            epa.append(float(v))
        df = pd.DataFrame({
            "VpA(A^3)": round_format(vpa, decimal),
            "EpA(eV)": round_format(epa, decimal)
        })

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table, df


class CohesiveReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        lattice = []
        epa = []
        cohesive_energy = []
        for k, m in res_data.items():
            lattice.append(float(k))
            epa.append(float(m["total_energy"]))
            cohesive_energy.append(float(m["cohesive_energy"]))
        
        df = pd.DataFrame({
            "ScaledLattice": lattice,
            "CohesiveEnergy(eV/atom)": cohesive_energy
        })
        
        trace = go.Scatter(
            name=name,
            x=df['ScaledLattice'],
            y=df['CohesiveEnergy(eV/atom)'],
            mode='lines+markers'
        )
        
        zero_line = go.Scatter(
            x=[min(lattice), max(lattice)],
            y=[0, 0],
            mode='lines',
            line=dict(color='blue', width=1, dash='dot'),
            showlegend=False
        )

        layout = go.Layout(
            title='Cohesive Energy',
            xaxis=dict(
                title_text="Scaled Lattice Parameter a/a<sub>0</sub>",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                ),
            ),
            yaxis=dict(
                title_text="Cohesive Energy E<sub>coh</sub> (eV/atom)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                ),
            )
        )
        
        return [trace, zero_line], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        lattice = []
        epa = []
        cohesive_energy = []
        for k, m in res_data.items():
            lattice.append(float(k))
            epa.append(float(m["total_energy"]))
            cohesive_energy.append(float(m["cohesive_energy"]))
            
        df = pd.DataFrame({
            "Scaled Lattice Parameter (a/a0)": round_format(lattice, decimal),
            "Total Energy (eV/atom)": round_format(epa, decimal),
            "Cohesive Energy (eV/atom)": round_format(cohesive_energy, decimal)
        })

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table, df
    
    
class DecohesiveReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        vacuum_size = [values[0] for values in res_data.values()]
        decohesion_e = [values[1] for values in res_data.values()]
        stress = [values[2] for values in res_data.values()]
        vacuum_size = [str(item) for item in vacuum_size]
        df = pd.DataFrame({
            "Separation Distance (A)": vacuum_size,
            "Decohesion Energy (J/m^2)": decohesion_e,
            "Decohesion Stress (GPa)": [s / 1e9 for s in stress],
        })
        trace_E = go.Scatter(
            name=f"{name} Decohesion Energy",
            x=df['Separation Distance (A)'],
            y=df['Decohesion Energy (J/m^2)'],
            mode='lines+markers',
            yaxis='y1'
        )

        trace_S = go.Scatter(
            name=f"{name} Decohesion Stress",
            x=df['Separation Distance (A)'],
            y=df['Decohesion Stress (GPa)'],
            mode='lines+markers',
            yaxis='y2'
        )
        layout = go.Layout(
            title=dict(
                text='Decohesion Energy and Stress',
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title_text="Separation Distance (A)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            ),
            yaxis=dict(
                title="Decohesion Energy (J/m^2)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            ),
            yaxis2=dict(
                title="Decohesion Stress (GPa)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                ),
                overlaying='y',
                side='right'
            )
        )
        trace = [trace_E, trace_S]
        return trace, layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        vacuum_size = [values[0] for values in res_data.values()]
        decohesion_e = [values[1] for values in res_data.values()]
        stress = [values[2] for values in res_data.values()]
        vacuum_size = [str(item) for item in vacuum_size]
        df = pd.DataFrame({
            "Separation Distance (A)": vacuum_size,
            "Decohesion Energy (J/m^2)": round_format(decohesion_e, decimal),
            "Decohesion Stress (GPa)": round_format([s / 1e9 for s in stress], decimal),
        })
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )
        return table, df


class Lat_param_T_Report(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        # Build a mapping temp(K) -> {a,b,c}
        data = {}
        for k, v in res_data.items():
            if isinstance(v, (list, tuple)) and len(v) >= 4:
                a, b, c, t = float(v[0]), float(v[1]), float(v[2]), float(v[3])
            elif isinstance(v, dict):
                a = float(v.get('a', 0.0)); b = float(v.get('b', 0.0)); c = float(v.get('c', 0.0)); t = float(v.get('temperature', 0.0))
            else:
                continue
            data[float(t)] = {'a': a, 'b': b, 'c': c}
        # Optional 0K from relaxation
        relax_abc = kwargs.get('relax_abc')
        if relax_abc and 0.0 not in data:
            a0, b0, c0 = relax_abc
            data[0.0] = {'a': float(a0), 'b': float(b0), 'c': float(c0)}
        # Sort by temperature
        temps = sorted(data.keys())
        xs = [str(int(t)) if abs(t-round(t))<1e-6 else str(t) for t in temps]
        ay = [data[t]['a'] for t in temps]
        by = [data[t]['b'] for t in temps]
        cy = [data[t]['c'] for t in temps]

        trace_a = go.Scatter(x=xs, y=ay, mode='lines+markers', name='a', line=dict(color='blue'))
        trace_b = go.Scatter(x=xs, y=by, mode='lines+markers', name='b', line=dict(color='green'))
        trace_c = go.Scatter(x=xs, y=cy , mode='lines+markers', name='c', line=dict(color='red'))

        layout = go.Layout(
            title='Lat_param_T (a,b,c vs T)',
            xaxis=dict(title='Temperature (K)'),
            yaxis=dict(title='Lattice length (Å)'),
            showlegend=True
        )
        return [trace_a, trace_b, trace_c], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 6, **kwargs) -> dash_table.DataTable:
        # Build structure temp->(a,b,c)
        data = {}
        for k, v in res_data.items():
            if isinstance(v, (list, tuple)) and len(v) >= 4:
                a, b, c, t = float(v[0]), float(v[1]), float(v[2]), float(v[3])
            elif isinstance(v, dict):
                a = float(v.get('a', 0.0)); b = float(v.get('b', 0.0)); c = float(v.get('c', 0.0)); t = float(v.get('temperature', 0.0))
            else:
                continue
            data[float(t)] = {'a': a, 'b': b, 'c': c}
        # Optional 0K from relaxation
        relax_abc = kwargs.get('relax_abc')
        if relax_abc and 0.0 not in data:
            a0, b0, c0 = relax_abc
            data[0.0] = {'a': float(a0), 'b': float(b0), 'c': float(c0)}
        temps = sorted(data.keys())
        rows = []
        for t in temps:
            a = data[t]['a']; b = data[t]['b']; c = data[t]['c']
            ca = (c/a) if a else 0.0
            rows.append({
                'Temp (K)': int(t) if abs(t-round(t))<1e-6 else t,
                'a (A)': round(a, decimal),
                'b (A)': round(b, decimal),
                'c (A)': round(c, decimal),
                'c/a': round(ca, decimal),
            })
        df = pd.DataFrame(rows)
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )
        return table, df

class AnnealingReport(PropertyReport):
    @staticmethod
    def _parse_interval_file(path):
        temps, vatoms, steps, potes, etots, press = [], [], [], [], [], []
        try:
            with open(path, 'r') as fp:
                for line in fp:
                    line=line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) < 6:
                        continue
                    try:
                        step = float(parts[0]); temp = float(parts[1]); vatom = float(parts[2])
                        pote = float(parts[3]); etot = float(parts[4]); prs = float(parts[5])
                    except Exception:
                        continue
                    steps.append(step); temps.append(temp); vatoms.append(vatom)
                    potes.append(pote); etots.append(etot); press.append(prs)
        except Exception:
            pass
        return steps, temps, vatoms, potes, etots, press

    @staticmethod
    def _parse_rdf_last_block(path):
        # Expect LAMMPS fix ave/time vector file with repeating blocks:
        # header; then: "<TimeStep> <Nrow>" followed by Nrow lines: "i r g coord".
        rs, gr = [], []
        try:
            with open(path, 'r') as fp:
                lines = [l.strip() for l in fp if l.strip()]
            # scan from end to find last "timestep nrow" header
            idx = len(lines)-1
            while idx >= 0:
                if lines[idx][0] == '#':
                    idx -= 1; continue
                head = lines[idx].split()
                if len(head) == 2 and head[0].isdigit():
                    # start of block
                    try:
                        nrow = int(head[1])
                    except Exception:
                        break
                    start = idx+1
                    block = lines[start:start+nrow]
                    rs = []; gr = []
                    for row in block:
                        cols = row.split()
                        if len(cols) >= 3:
                            try:
                                r = float(cols[1]); g = float(cols[2])
                            except Exception:
                                continue
                            rs.append(r); gr.append(g)
                    break
                idx -= 1
        except Exception:
            pass
        return rs, gr

    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        import os
        prop_dir = kwargs.get('prop_dir')
        # aggregate all tasks
        heat_T, heat_V = [], []
        cool_T, cool_V = [], []
        rdf_r, rdf_g = [], []
        if prop_dir and os.path.isdir(prop_dir):
            tasks = [t for t in os.listdir(prop_dir) if t.startswith('task.') and os.path.isdir(os.path.join(prop_dir, t))]
            tasks.sort()
            for t in tasks:
                tdir = os.path.join(prop_dir, t)
                hs = os.path.join(tdir, 'heating_interval.dat')
                cs = os.path.join(tdir, 'cooling_interval.dat')
                if os.path.isfile(hs):
                    _, T, V, *_ = AnnealingReport._parse_interval_file(hs)
                    heat_T.extend(T); heat_V.extend(V)
                if os.path.isfile(cs):
                    _, T, V, *_ = AnnealingReport._parse_interval_file(cs)
                    cool_T.extend(T); cool_V.extend(V)
                if not rdf_r:  # take first available rdf
                    rc = os.path.join(tdir, 'rdf_cool.dat')
                    if os.path.isfile(rc):
                        rdf_r, rdf_g = AnnealingReport._parse_rdf_last_block(rc)

        traces = []
        # scatter: Vatom vs Temp
        if heat_T and heat_V:
            traces.append(go.Scatter(x=heat_T, y=heat_V, mode='markers', name=f'{name} Heating',
                                     marker=dict(color='rgb(239,85,59)', size=6)))  # warm
        if cool_T and cool_V:
            traces.append(go.Scatter(x=cool_T, y=cool_V, mode='markers', name=f'{name} Cooling',
                                     marker=dict(color='rgb(31,119,180)', size=6)))  # cool
        # RDF: g(r)
        if rdf_r and rdf_g:
            traces.append(go.Scatter(x=rdf_r, y=rdf_g, mode='lines', name=f'{name} g(r)',
                                     xaxis='x2', yaxis='y2', line=dict(color='rgb(99,110,250)')))

        layout = go.Layout(
            title='Annealing Summary',
            xaxis=dict(title='Temperature (K)', domain=[0.0, 1.0]),
            yaxis=dict(title='Vatom (A^3/atom)', domain=[0.55, 1.0]),
            xaxis2=dict(title='r (Å)', domain=[0.0, 1.0], anchor='y2'),
            yaxis2=dict(title='g(r)', domain=[0.0, 0.45])
        )
        return traces, layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 6, **kwargs) -> dash_table.DataTable:
        import os
        prop_dir = kwargs.get('prop_dir')
        rows = []
        if prop_dir and os.path.isdir(prop_dir):
            tasks = [t for t in os.listdir(prop_dir) if t.startswith('task.') and os.path.isdir(os.path.join(prop_dir, t))]
            tasks.sort()
            for t in tasks:
                tdir = os.path.join(prop_dir, t)
                for stage, fname in [('heating', 'heating_interval.dat'), ('cooling', 'cooling_interval.dat')]:
                    f = os.path.join(tdir, fname)
                    if not os.path.isfile(f):
                        continue
                    steps, temps, vatoms, potes, etots, press = AnnealingReport._parse_interval_file(f)
                    for s, T, V, pe, et, pr in zip(steps, temps, vatoms, potes, etots, press):
                        rows.append({
                            'Task': t,
                            'Stage': stage,
                            'TimeStep': int(s) if abs(s-round(s))<1e-6 else s,
                            'Temp (K)': round(T, decimal),
                            'Vatom (A^3/atom)': round(V, decimal),
                            'pote (eV)': round(pe, decimal),
                            'Etotal (eV)': round(et, decimal),
                            'Press': round(pr, decimal),
                        })
        df = pd.DataFrame(rows)
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )
        return table, df

class ElasticReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        elastic_tensor = res_data['elastic_tensor']
        c11 = elastic_tensor[0][0]
        c12 = elastic_tensor[0][1]
        c13 = elastic_tensor[0][2]
        c22 = elastic_tensor[1][1]
        c23 = elastic_tensor[1][2]
        c33 = elastic_tensor[2][2]
        c44 = elastic_tensor[3][3]
        c55 = elastic_tensor[4][4]
        c66 = elastic_tensor[5][5]
        BV = res_data['B']
        GV = res_data['G']
        EV = res_data['E']
        uV = res_data['u']

        polar = go.Scatterpolar(
            name=name,
            r=[c11, c12, c13, c22, c23, c33,
               c44, c55, c66, BV, GV, EV, uV],
            theta=['C11', 'C12', 'C13', 'C22', 'C23', 'C33',
                   'C44', 'C55', 'C66', 'B', 'G', 'E', 'u'],
            fill='none'
        )

        layout = go.Layout(
            showlegend=True,
            title='Elastic Property'
        )

        return [polar], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        ph = '-'
        et = res_data['elastic_tensor']
        BV = res_data['B']
        GV = res_data['G']
        EV = res_data['E']
        uV = res_data['u']
        null_t = [' '] * 6
        BV_t = ['B', BV, ph, ph, ph, ph]
        GV_t = ['G', GV, ph, ph, ph, ph]
        EV_t = ['E', EV, ph, ph, ph, ph]
        uV_t = ['u', uV, ph, ph, ph, ph]
        table_tensor = [et[0], et[1], et[2], et[3], et[4], et[5],
                        null_t, BV_t, GV_t, EV_t, uV_t]

        # round numbers in table
        rounded_tensor = round_2d_format(table_tensor, decimal)

        df = pd.DataFrame(
            rounded_tensor,
            columns=['Col 1', 'Col 2', 'Col 3', 'Col 4', 'Col 5', 'Col 6'],
        )

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'width': '150px'}
        )

        return table, df


class CohesiveEnergyReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        lattice = []
        cohesive_energy = []
        for k, v in res_data.items():
            lattice.append(float(k))
            cohesive_energy.append(float(v))
            
        a0 = lattice[0] if lattice else 1.0
        scaled_lattice = [a/a0 for a in lattice]
        
        df = pd.DataFrame({
            "Scaled Lattice Parameter": scaled_lattice,
            "Cohesive Energy": cohesive_energy
        })
        
        line_style = kwargs.get('line_style', 'solid')
        marker_symbol = kwargs.get('marker_symbol', 'circle')
        line_color = kwargs.get('line_color', random_color())
        line_width = kwargs.get('line_width', 2)
        
        trace = go.Scatter(
            name=name,
            x=df['Scaled Lattice Parameter'],
            y=df['Cohesive Energy'],
            mode='lines+markers',
            line=dict(color=line_color, width=line_width, dash=line_style),
            marker=dict(symbol=marker_symbol, size=8)
        )
        
        zero_line = go.Scatter(
            x=[min(scaled_lattice), max(scaled_lattice)],
            y=[0, 0],
            mode='lines',
            line=dict(color='blue', width=1, dash='dot'),
            showlegend=False
        )
        
        layout = go.Layout(
            title='Cohesive Energy',
            xaxis=dict(
                title_text="Scaled lattice parameter a/a<sub>0</sub>",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                ),
                range=[0.5, 2.5]  
            ),
            yaxis=dict(
                title_text="Cohesive energy E<sub>coh</sub> (eV/atom)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                ),
                range=[-7, 8]  
            ),
            showlegend=True,
            legend=dict(
                x=0.7,
                y=0.9,
                bgcolor='rgba(255, 255, 255, 0.5)'
            )
        )
        
        return [trace, zero_line], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        lattice = []
        cohesive_energy = []
        for k, v in res_data.items():
            lattice.append(float(k))
            cohesive_energy.append(float(v))
            
        a0 = lattice[0] if lattice else 1.0
        scaled_lattice = [a/a0 for a in lattice]
            
        df = pd.DataFrame({
            "Lattice Constant (Å)": round_format(lattice, decimal),
            "Scaled Lattice Parameter (a/a0)": round_format(scaled_lattice, decimal),
            "Cohesive Energy (eV/atom)": round_format(cohesive_energy, decimal)
        })

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table, df


class SurfaceReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        miller = []
        surf_e = []
        epa = []
        epa_equi = []
        for k, v in res_data.items():
            miller.append(k.split('_')[0])
            surf_e.append(float(v[0]))
            epa.append(float(v[1]))
            epa_equi.append(float(v[2]))

        # enclose polar plot
        surf_e.append(surf_e[0])
        miller.append(miller[0])
        polar = go.Scatterpolar(
            name=name,
            r=surf_e,
            theta=miller,
            fill='none'
        )

        layout = go.Layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    autorange=True
                )
            ),
            showlegend=True,
            title='Surface Forming Energy'
        )

        return [polar], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        miller = []
        surf_e = []
        epa = []
        epa_equi = []
        for k, v in res_data.items():
            miller.append(k.split('_')[0])
            surf_e.append(float(v[0]))
            epa.append(float(v[1]))
            epa_equi.append(float(v[2]))
        df = pd.DataFrame({
            "Miller Index": miller,
            "E_surface (J/m^2)": round_format(surf_e, decimal),
            "EpA (eV)": round_format(epa, decimal),
            "EpA_equi (eV)": round_format(epa_equi, decimal),
        })

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table, df


class InterstitialReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        inter_struct = []
        inter_form_e = []
        struct_e = []
        equi_e = []
        for k, v in res_data.items():
            inter_struct.append(k.split('_')[1])
            inter_form_e.append(float(v[0]))
            struct_e.append(float(v[1]))
            equi_e.append(float(v[2]))

        # enclose polar plot
        inter_struct.append(inter_struct[0])
        inter_form_e.append(inter_form_e[0])

        polar = go.Scatterpolar(
            name=name,
            r=inter_form_e,
            theta=inter_struct,
            fill='none'
        )

        layout = go.Layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    autorange=True
                )
            ),
            showlegend=True,
            title='Interstitial Forming Energy'
        )

        return [polar], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        inter_struct = []
        inter_form_e = []
        struct_e = []
        equi_e = []
        for k, v in res_data.items():
            inter_struct.append(k.split('_')[1])
            inter_form_e.append(float(v[0]))
            struct_e.append(float(v[1]))
            equi_e.append(float(v[2]))
        df = pd.DataFrame({
            "Initial configuration ": inter_struct,
            "E_form (eV)": round_format(inter_form_e, decimal),
            "E_defect (eV)": round_format(struct_e, decimal),
            "E_equi (eV)": round_format(equi_e, decimal),
        })

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table, df


class VacancyReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        v = list(res_data.values())[0]
        vac_form_e = float(v[0])
        struct_e = float(v[1])
        equi_e = float(v[2])

        bar = go.Bar(
            name=name,
            # x=[vac_form_e, struct_e, equi_e],
            # y=['E_form (eV)', 'E_defect (eV)', 'E_equi (eV)'],
            x=[vac_form_e],
            y=['E_form'],
            orientation='h'
        )

        layout = go.Layout(
            title='Vacancy Forming Energy',
            xaxis=dict(
                title_text="Vacancy Forming Energy (eV)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            ),
            yaxis=dict(
                title_text="",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                ),
            ),
            showlegend=True
        )

        return [bar], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        vac_form_e = []
        struct_e = []
        equi_e = []
        for k, v in res_data.items():
            vac_form_e.append(float(v[0]))
            struct_e.append(float(v[1]))
            equi_e.append(float(v[2]))
        df = pd.DataFrame({
            "E_form (eV)": round_format(vac_form_e, decimal),
            "E_defect (eV)": round_format(struct_e, decimal),
            "E_equi (eV)": round_format(equi_e, decimal),
        })

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table, df


class GammaReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        displ = []
        displ_length = []
        fault_en = []
        struct_en = []
        equi_en = []
        for k, v in res_data.items():
            displ.append(k)
            displ_length.append(v[0])
            fault_en.append(v[1])
            struct_en.append((v[2]))
            equi_en.append(v[3])
        df = pd.DataFrame({
            "displacement": displ,
            "displace_length": displ_length,
            "fault_en": fault_en
        })
        trace = go.Scatter(
            name=name,
            x=df['displacement'],
            # x=df['displace_length'],
            y=df['fault_en'],
            mode='lines+markers'
        )
        layout = go.Layout(
            title='Stacking Fault Energy (Gamma Line)',
            xaxis=dict(
                title_text="Slip Fraction",
                # title_text="Displace_Length (Å)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            ),
            yaxis=dict(
                title_text='Fault Energy (J/m<sup>2</sup>)',
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            )
        )

        return [trace], layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        displ = []
        displ_length = []
        fault_en = []
        struct_en = []
        equi_en = []
        for k, v in res_data.items():
            displ.append(float(k))
            displ_length.append(v[0])
            fault_en.append(v[1])
            struct_en.append((v[2]))
            equi_en.append(v[3])
        df = pd.DataFrame({
            "Slip_frac": round_format(displ, decimal),
            "Slip_Length (Å)": round_format(displ_length, decimal),
            "E_Fault (J/m^2)": round_format(fault_en, decimal),
            "E_Slab (eV)": round_format(struct_en, decimal),
            "E_Equilib (eV)": round_format(equi_en, decimal)
        })

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table, df


class PhononReport(PropertyReport):
    @staticmethod
    def plotly_graph(res_data: dict, name: str, **kwargs):
        bands = res_data['band']

        band_path_list = []
        for seg in bands[0]:
            seg_list = [k for k in seg.keys()]
            band_path_list.extend(seg_list)
        band_list = []
        for band in bands:
            seg_result_list = []
            for seg in band:
                seg_result = [v for v in seg.values()]
                seg_result_list.extend(seg_result)
            band_list.append(seg_result_list)
        pd_dict = {"Band Path": band_path_list}
        for ii in range(len(band_list)):
            pd_dict['Band %02d' % (ii + 1)] = band_list[ii]
        df = pd.DataFrame(pd_dict)
        traces = []


        for ii in range(len(band_list)):
            trace = go.Scatter(
                x=df['Band Path'],
                y=df['Band %02d' % (ii + 1)],
                name='Band %02d' % (ii + 1),
                legendgroup=name,
                legendgrouptitle_text=name,
                mode='lines',
                line=dict(color=kwargs["color"], width=1.5)
            )
            traces.append(trace)

        segment_value_list = res_data['segment']
        band_path_info = res_data['band_path']
        segment_value_iter = iter(segment_value_list)

        x_label_list = []
        connect_seg = False
        pre_k = None
        for seg in band_path_info:
            for point in seg:
                k = list(point.keys())[0]
                if connect_seg:
                    new_k = f'{pre_k}/{k}'
                    x_label_list[-1][0] = new_k
                    connect_seg = False
                else:
                    x_label_list.append([k, float(next(segment_value_iter))])
            pre_k = k
            connect_seg = True

        # label special points
        x_label_values_list = [x[1] for x in x_label_list]
        annotations = []
        shapes = []

        for x_label in x_label_list:
            # add label
            annotations.append(go.layout.Annotation(
                x=x_label[1],
                y=1.08,
                xref="x",
                yref="paper",
                text=x_label[0],  # label text
                showarrow=False,
                yshift=0,  # label position
                xanchor='center'
            ))

            # add special vertical line
            '''
            shapes.append({
                'type': 'line',
                'x0': x_label[1],
                'y0': 0,
                'x1': x_label[1],
                'y1': 1,
                'xref': 'x',
                'yref': 'paper',
                'line': {
                    'color': 'grey',
                    'width': 1,
                    'dash': 'dot',
                },
            })
            '''

        layout = go.Layout(
            title='Phonon Spectra',
            annotations=annotations,
            shapes=shapes,
            autotypenumbers='convert types',
            xaxis=dict(
                tickmode='array',
                tickvals=x_label_values_list,
                ticktext=[f'{float(val):.3f}' for val in x_label_values_list],
                title_text="Band Path",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            ),
            yaxis=dict(
                title_text="Frequency (THz)",
                title_font=dict(
                    size=18,
                    color="#7f7f7f"
                )
            )
        )

        return traces, layout

    @staticmethod
    def dash_table(res_data: dict, decimal: int = 3, **kwargs) -> dash_table.DataTable:
        bands = res_data['band']
        band_path_list = []
        for seg in bands[0]:
            seg_list = [float(k) for k in seg.keys()]
            band_path_list.extend(seg_list)
            band_path_list.append(' ')
        band_path_list.pop()

        band_list = []
        for band in bands:
            seg_result_list = []
            for seg in band:
                seg_result = [v for v in seg.values()]
                seg_result_list.extend(seg_result)
                seg_result_list.append(' ')
            seg_result_list.pop()
            band_list.append(round_format(seg_result_list, decimal))

        pd_dict = {"Band Path": round_format(band_path_list, decimal)}
        for ii in range(len(band_list)):
            pd_dict['Band %02d' % (ii + 1)] = band_list[ii]

        df = pd.DataFrame(pd_dict)

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'width': TABLE_WIDTH,
                         'minWidth': TABLE_MIN_WIDTH,
                         'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table, df
