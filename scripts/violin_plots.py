from enum import IntEnum
import re
import sys
import argparse
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
from distinctipy import distinctipy
from os import listdir
from os.path import isfile, join

mpl.use('pdf')
# import scienceplots
# plt.style.use(['science', 'ieee'])

SEPARATE_ROBOTS = True
USE_MONTREAL_DATA = True

FIRST_ROW = 0
FINAL_ROW = 6000

# width as measured in inkscape
width = 8  # 3.487
if SEPARATE_ROBOTS:
    # height = width * 2
    height = width / 1.5
else:
    height = width / 1.5
    RHOS = [0.5, 0.6, 0.7, 0.8, 0.9]

if USE_MONTREAL_DATA:
    HEADER_STR = "DeliveryLog_m6_rho99"
    OUTPUT_PREFIX = "Montreal_RAL"
    ROBOTS = 6
else:
    HEADER_STR = "DeliveryLog_ral"
    OUTPUT_PREFIX = "RAL"
    ROBOTS = 1

HEADER_SUBSTR = ""


def export_table2(df, hues):

    print('%%%%%')
    print('% Table Data for Uniform Distribution in metric space')
    print('%')
    print('\\begin{table*}')
    print('\\caption{Mean, Median and Average Task Wait Times (m)}')
    print('\\label{table:task-time-data}')
    print('\\begin{center}')

    column_str = '\\begin{tabular}{@{} l'
    heading_str = ' '
    heading2_str = 'Method '
    if SEPARATE_ROBOTS:
        for r in range(ROBOTS):
            column_str += ' c c '
            heading_str += f'& \\multicolumn{{2}}{{c}}{r+1} '
            heading2_str += ' & Mean\\rpm $\\sigma$ & 95\% '

        column_str += ' c c '
        heading_str += f'& \\multicolumn{{2}}{{c}}{{Unified}}'
        heading2_str += ' & Mean\\rpm $\\sigma$ & 95\% '
    else:
        for rho in RHOS:
            column_str += ' c c '
            heading_str += f'& \\multicolumn{{2}}{{c}}{rho} '
            heading2_str += ' & Mean\\rpm $\\sigma$ & 95\% '
    column_str += ' @{}}'
    heading_str += ' \\\\'
    heading2_str += ' \\\\'

    print(column_str)
    print('\\toprule')
    print(heading_str)
    print(heading2_str)

    print('\\midrule')

    for index, hue in enumerate(hues):
        s = hue
        rho = 0.9
        if SEPARATE_ROBOTS:
            for robot in range(1, ROBOTS+1):
                # df_slice = df[(df['Solver'] == hue) & (df['cluster'] == robot) & (df['rho'] == rho)]
                df_slice = df[(df['Solver'] == hue) & (df['cluster_remap'] == robot)]
                s += ' & ' + \
                    f"{round(df_slice['wait_minutes'].mean())}\\rpm{round(df_slice['wait_minutes'].std())} & {round(df_slice['wait_minutes'].quantile(q=0.95))}"
            # df_slice = df[(df['Solver'] == hue) & (df['rho'] == rho)]
            df_slice = df[(df['Solver'] == hue)]
            s += '& ' + \
                f"{round(df_slice['wait_minutes'].mean())}\\rpm{round(df_slice['wait_minutes'].std())} & {round(df_slice['wait_minutes'].quantile(q=0.95))}"
        else:
            for rho in RHOS:
                df_slice = df[(df['Solver'] == hue) & (df['rho'] == rho)]
                if USE_MONTREAL_DATA:
                    s += ' & ' + \
                        f"{(df_slice['wait_minutes'].mean()):5.1f} \\rpm {(df_slice['wait_minutes'].std()):5.1f} & {(df_slice['wait_minutes'].quantile(q=0.95)):5.1f}"
                else:
                    s += ' & ' + \
                        f"{(df_slice['Wait Time'].mean()):5.1f} \\rpm {(df_slice['Wait Time'].std()):5.1f} & {(df_slice['Wait Time'].quantile(q=0.95)):5.1f}"
        s += "\\\\"
        print(s)
        if index == 1:
            # hacky bit to insert a line after the second row
            print('\\midrule')

    print('\\bottomrule')
    print('\\end{tabular}')
    print('\\end{center}')
    print('\\end{table*}')
    print('%')
    print('%%%%%')


def export_table(df, hues):

    print('%%%%%')
    print('% Table Data for Uniform Distribution in metric space')
    print('%')
    print('\\begin{table}')
    print('\\caption{Mean, Median and Average Task Wait Times (s)}')
    print('\\label{table:task-time-data}')
    print('\\begin{center}')
    print('\\begin{tabular}{@{} l l c c c c @{}}')
    print('\\toprule')
    print('$\\rho$ & Method & Mean & Median & $\\sigma$ & 95\% \\\\')

    if USE_MONTREAL_DATA:
        for cluster in range(ROBOTS):
            print('\\midrule')
            rho_str = str(cluster)
            for hue in hues:
                df_slice = df[(df['Solver'] == hue) & (df['cluster'] == cluster)]
                print(
                    f"{rho_str} & {hue} & {(df_slice['wait_minutes'].mean()):5.1f} & {(df_slice['wait_minutes'].median()):5.1f} & {(df_slice['wait_minutes'].std()):5.1f} & {(df_slice['wait_minutes'].quantile(q=0.95)):5.1f} \\\\")
            rho_str = ''
    else:
        for rho in [0.5, 0.6, 0.7, 0.8, 0.9]:
            print('\\midrule')
            rho_str = str(rho)
            for hue in hues:
                df_slice = df[(df['Solver'] == hue) & (df['rho'] == rho)]
                print(
                    f"{rho_str} & {hue} & {(df_slice['Wait Time'].mean()):5.1f} & {(df_slice['Wait Time'].median()):5.1f} & {(df_slice['Wait Time'].std()):5.1f} & {(df_slice['Wait Time'].quantile(q=0.95)):5.1f} \\\\")
            rho_str = ''

    print('\\bottomrule')
    print('\\end{tabular}')
    print('\\end{center}')
    print('\\end{table}')
    print('%')
    print('%%%%%')


def reconstruct_policy_label(tags, meta_data, offset):
    # print(tags)
    if tags[offset-6] == 'time':
        tags.pop(offset-6)

    if tags[offset-6] == 'trp':
        if tags[offset-7] == 'cont':
            return '$c^2$-$\mathtt{EVENT}$'
        else:
            if meta_data['eta'] == 0.05:
                return '$\mathtt{PROPOSED}$'
            else:
                return '$\mathtt{PROPOSED}$ $\eta$=$'+str(meta_data['eta']) + '$'
                # return '$c^p$-$\mathtt{BATCH}$ $\eta$=$'+str(meta_data['eta']) + '$ $p$=$'+str(meta_data['p'])+'$'
            # return '$\mathtt{PROPOSED}$ $\eta$=$'+str(meta_data['eta']) + '$'
            # return '$c^p$-$\mathtt{BATCH}$ $\eta$=$'+str(meta_data['eta']) + '$ $p$=$'+str(meta_data['p'])+'$'
        # return 'LKH-Batch-TRP'
    elif tags[offset-6] == 'tsp':
        if tags[offset-7] == 'batch':
            if meta_data['sectors'] > 1.0:
                return '$\mathtt{DC}$-$\mathtt{BATCH}$'  # , $\eta=' + str(meta_data['eta']) + '$, $r=' + str(meta_data['sectors'])+'$'
            else:
                if meta_data['eta'] == 1:
                    return '$\mathtt{BATCH}$'
                else:
                    return '$\eta$-$\mathtt{BATCH}$'
        else:
            return '$\mathtt{Event}$ $p$=$1.5$'
    return 'None'


def plot_comparison(files, mode='baselines'):

    sb.set_theme(style="whitegrid")
    sb.set()

    plt.rc('font', family='serif', serif='Times')
    plt.rc('text', usetex=True)
    plt.rc('xtick', labelsize=16)
    plt.rc('ytick', labelsize=16)
    plt.rc('axes', labelsize=12)

    df_list = []
    for f in files:
        if HEADER_STR in f and HEADER_SUBSTR in f:
            # if 'DeliveryLog' in f and 'icra_v6_lkh_batch_trp' in f:       # ICRA/OLD data
            df = pd.read_csv(f)

            # slice the rows we want
            df = df.loc[FIRST_ROW:FINAL_ROW]

            try:
                df['cost-exponent'] = df['cost_exponent']
            except KeyError:
                pass
            if not 'sectors' in df.columns:
                df['sectors'] = 1

            tags = f.split('_')  # get meta data
            offset = 1 if '1.0t' in tags[-1] else 0

            if tags[offset-6][-2:] == 'sc':
                sectors = int(tags[offset-6][0:-2])
                tags.pop(offset-6)
            else:
                sectors = 1

            eta = tags[offset-4]
            eta = float(eta.strip('ef'))

            meta_data = {'lambda': float(tags[offset-3][0:-1]),                                              # tagged 'l'
                         'eta': eta,
                         'p': float(tags[offset-5][0:-1]) if float(tags[offset-5][0:-1]) != -5 else 1.5,       # tagged 'p'
                         'sectors': sectors,                                                                 # tagged 'sc'
                         }

            meta_data['Solver'] = reconstruct_policy_label(tags, meta_data, offset)
            for key in meta_data.keys():
                df[key] = meta_data[key]
            df['Wait Time'] = df['t_service'] - df['t_arrive']
            df['Seed'] = tags[-1]

            # TODO: Hardcoding the base delivery time if
            service_time = tags[offset-2][:-1]
            # df['rho'] = np.round((291 + float(service_time)) * meta_data['lambda'], 2)
            df['rho'] = np.round((float(service_time)) * meta_data['lambda'] / ROBOTS, 2)
            df['wait_minutes'] = np.round(df['Wait Time']/60.0, 2)
            df_list.append(df)

    df = pd.concat(df_list, ignore_index=True, sort=False)

    if SEPARATE_ROBOTS:
        cluster_map = [1, 5, 6, 2, 3, 4]
        df['cluster_remap'] = 0
        for cluster, cluster_remap in enumerate(cluster_map):
            df.loc[df['cluster'] == cluster, 'cluster_remap'] = int(cluster_remap)

    graphs = [(0.5, 0.9, 'high')]
    # graphs = [(0.5, 0.7, 'high')]
    # graphs = [(0.7, 0.7, 'high')]

    if mode == 'baselines':

        if USE_MONTREAL_DATA:
            colours = [
                'darkorange',
                # 'wheat',
                'lightsteelblue',
                'royalblue',
                'lavender',
                'slateblue',


                'dodgerblue',
                # 'bisque',
                'linen'
            ]

            hue_order = [
                '$\mathtt{PROPOSED}$',
                # '$\mathtt{PROPOSED}$ $\eta$=$0.2$',
                '$c^2$-$\mathtt{EVENT}$',
                '$\mathtt{BATCH}$',
                '$\mathtt{DC}$-$\mathtt{BATCH}$',
                '$\eta$-$\mathtt{BATCH}$',
            ]
        else:
            colours = [
                'darkorange',
                # 'wheat',
                'lightsteelblue',
                'royalblue',
                'lavender',
                'slateblue',


                'dodgerblue',
                # 'bisque',
                'linen'
            ]

            hue_order = [
                '$\mathtt{PROPOSED}$',
                # '$\mathtt{PROPOSED}$ $\eta$=$0.2$',
                '$c^2$-$\mathtt{EVENT}$',
                '$\mathtt{BATCH}$',
                '$\mathtt{DC}$-$\mathtt{BATCH}$',
                '$\eta$-$\mathtt{BATCH}$',
            ]

        # seeds = set(df['Seed'])
        # rhos = set(df['rho'])

        # for hue in hue_order:
        #     for rho in rhos:
        #         for seed in seeds:
        #             row_mask = (df['Solver'] == hue) & (df['Seed'] == seed) & (df['rho'] == rho)
        #             df_d = df.loc[(df['Solver'] == '$\mathtt{BATCH}$') & (df['Seed'] == seed) & (df['rho'] == rho)]
        #             batch_mean = df_d['Wait Time'].mean()

        #             df_n = df.loc[row_mask]

        #             df.loc[row_mask, 'normalized-wait'] = df_n['Wait Time'].to_numpy() / batch_mean

    elif mode == 'differentP':
        hue_order = [
            '$c^p$-$\mathtt{BATCH}$ $\eta$=$0.2$ $p$=$1.0$',
            # '$c^p - \mathtt{BATCH}$, $\eta=0.2$, $p=1.1$',
            '$c^p$-$\mathtt{BATCH}$ $\eta$=$0.2$ $p$=$1.5$',
            '$c^p$-$\mathtt{BATCH}$ $\eta$=$0.2$ $p$=$2.0$',
            '$c^p$-$\mathtt{BATCH}$ $\eta$=$0.2$ $p$=$3.0$',
            # '$c^p - \mathtt{BATCH}$, $\eta=0.2$, $p=5.0$',
            '$c^p$-$\mathtt{BATCH}$ $\eta$=$0.2$ $p$=$10.0$',
        ]

        colours = [
            'lightblue',
            # 'slateblue',
            # 'lavender',
            'wheat',
            'violet',
            # 'bisque',
            'aliceblue',
            'dodgerblue',
            'aquamarine',
        ]
    elif mode == 'Variance':
        hue_order = [
            '$c^p$-$\mathtt{BATCH}$ $\eta=0.2$, $p=1.5$',
            # '$c^p - \mathtt{BATCH}$, $\eta=0.2$, $p=5.0$',
            '$\eta$-$\mathtt{BATCH}$ $\eta=1.0$',
            # '$\eta - \mathtt{BATCH}$, $\eta=1.0$, $r=4$',
            #  '$\eta - \mathtt{BATCH}$, $\eta=0.5$',
            '$\eta$-$\mathtt{BATCH}$ $\eta=0.2$',
            # 'DC-$\mathtt{BATCH}$, $\eta=1.0$, $r=10$',
        ]

        colours = [
            'deepskyblue',
            # 'slateblue',
            # 'lavender',
            'darkorange',
            'lightsteelblue',
            # 'bisque',
            'cyan',
            'mediumpurple',
            'aquamarine',
        ]
    else:
        print('No PIC for you! Two weeks!!')
        return

    # df_trim = []
    # for hue in hue_order:
    #     df_hue = df.loc[df['Solver'] == hue]
    #     df_hue = df_hue.iloc[-100000:-1000, :]
    #     df_trim.append(df_hue)
    # df = pd.concat(df_trim, ignore_index=True, sort=False)

    df_var = pd.DataFrame(columns=['hue', 'rho', 'mean', 'var'])

    if mode == 'Variance':
        rhos = [0.5, 0.6, 0.7, 0.8, 0.9]
        for hue in hue_order:
            for rho in rhos:
                df_slice = df[(df['rho'] == rho)]
                df_slice = df_slice[(df_slice['Solver'] == hue)]
                df_var = pd.concat([pd.DataFrame([[hue, rho, df_slice['Wait Time'].mean(), df_slice['Wait Time'].var()]],
                                                 columns=df_var.columns), df_var], ignore_index=True)

        print(df_var)

        fig, ax = plt.subplots()
        fig.subplots_adjust(left=.15, bottom=.16, right=.99, top=.97)
        sb.lineplot(x='rho', y='mean', hue='hue', data=df_var, linewidth=2.5)

        ax.set_yscale('log')
        ax.set_xlabel("$\\rho$", fontsize=20)
        ax.set_ylabel("Variance", fontsize=20)
        ax.tick_params(axis='both', which='major', labelsize=16)
        ax.legend(title='Method/Exponent', title_fontsize=18, fontsize=16)
        fig.set_size_inches(width, height)
        fig.savefig('VariancePlot.pdf')

        plt.show()
        return

    styles = ['Box']
    for style in styles:
        for l, h, label in graphs:
            sb.set_style(style="whitegrid")
            if SEPARATE_ROBOTS:
                fig, ax = plt.subplots()
                # fig, ax = plt.subplots(ROBOTS, 1)
                # fig, ax = plt.subplots()
            else:
                fig, ax = plt.subplots()
            fig.subplots_adjust(left=.15, bottom=.16, right=.99, top=.97)

            # sb.lineplot(x='lambda', y=col, hue='display-name', data=df_slice, palette=colours, linewidth=2.5)
            # if style == 'Violins':
            #     sb.violinplot(x='lambda', y='Wait Time', hue='Solver', hue_order=hue_order, data=df_slice, cut=0,
            #                   inner=None, palette=colours)
            #     ax.set_ylim([-10,300])
            if style == 'Box':
                flierprops = dict(marker='o', markerfacecolor='grey', markersize=2, alpha=.5,
                                  linestyle='none')
                if SEPARATE_ROBOTS:
                    # for robot in range(ROBOTS):
                    #     df_slice = df[df['cluster'] == robot]
                    #     sb.boxplot(ax=ax[robot], x='rho', y='wait_minutes', hue='Solver', hue_order=hue_order, data=df_slice,  showfliers=False, whis=0,
                    #                showmeans=True, palette=colours, flierprops=flierprops)
                    #     ax[robot].set_ylim([-1, 700])
                    #     ax[robot].set_xlabel("$\\rho$", fontsize=20)
                    df_slice = df  # df[df['rho'] == 0.9]
                    sb.boxplot(x='cluster_remap', y='wait_minutes', hue='Solver', hue_order=hue_order, data=df_slice,  showfliers=False, whis=[5, 95],
                               showmeans=True, palette=colours, flierprops=flierprops)
                    ax.set_ylim([-1, 2700])
                    ax.set_xlabel("Cluster", fontsize=20)
                else:
                    df_slice = df[(df['rho'] >= l) * (df['rho'] <= h)]
                    if USE_MONTREAL_DATA:
                        sb.boxplot(x='rho', y='wait_minutes', hue='Solver', hue_order=hue_order, data=df_slice,  showfliers=False, whis=0,
                                   showmeans=True, palette=colours, flierprops=flierprops)
                        ax.set_ylim([-1, 700])
                        ax.set_xlabel("$\\rho$", fontsize=20)
                    else:
                        sb.boxplot(x='rho', y='Wait Time', hue='Solver', hue_order=hue_order, data=df_slice,  showfliers=False, whis=1,
                                   showmeans=True, palette=colours, flierprops=flierprops)
                        ax.set_ylim([-1, 120])
                        ax.set_xlabel("$\\rho$", fontsize=20)
                # sb.boxplot(x='rho', y='normalized-wait', hue='Solver', hue_order=hue_order, data=df_slice,  showfliers=False,
                #            showmeans=True, palette=colours, flierprops=flierprops, whis=0)
                # ax.set_ylim([0, 2])

            if SEPARATE_ROBOTS:
                ax.set_ylabel("Wait Time (m)", fontsize=20)
                ax.tick_params(axis='both', which='major', labelsize=16)
                handles, labels = ax.get_legend_handles_labels()
                # ax.set_yscale('log')
                ax.legend(handles=handles, labels=labels, loc='upper left', title='Method/Exponent', title_fontsize=18, fontsize=16)
                # for robot in range(ROBOTS):
                #     ax[robot].set_ylabel("Time (m)", fontsize=20)
                #     ax[robot].tick_params(axis='both', which='major', labelsize=16)
                #     handles, labels = ax[robot].get_legend_handles_labels()
                #     # ax.set_yscale('log')
                #     # ax[robot].legend(handles=handles, labels=labels, loc='upper left', title='Method/Exponent', title_fontsize=18, fontsize=16)
            else:
                if USE_MONTREAL_DATA:
                    ax.set_ylabel("Wait Time (m)", fontsize=20)
                else:
                    ax.set_ylabel("Wait Time (s)", fontsize=20)
                ax.tick_params(axis='both', which='major', labelsize=16)
              # ax.set_ylabel("vs. BATCH Baseline", fontsize=20)

                handles, labels = ax.get_legend_handles_labels()
                # ax.set_yscale('log')

                ax.legend(handles=handles, labels=labels, loc='upper left', title='Method/Exponent', title_fontsize=18, fontsize=16)

            fig.set_size_inches(width, height)
            if SEPARATE_ROBOTS:
                separated = '_separated_'
            else:
                separated = ''
            fig.savefig(OUTPUT_PREFIX+separated+'_'+style+'_'+mode+'_plot_lamda_{}_{}.pdf'.format('WaitTime', label))

    # export_table(df, hues=hue_order)
    export_table2(df, hues=hue_order)


if __name__ == "__main__":

    path = 'results/'
    files = [path + '/' + f for f in listdir(path) if isfile(join(path, f))]
    plot_comparison(files, 'baselines')
    # plot_comparison(files, 'differentP')
    # plot_comparison(files, 'Variance')
