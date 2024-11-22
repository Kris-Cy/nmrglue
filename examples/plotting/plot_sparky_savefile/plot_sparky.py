#! /usr/bin/env python
"""
Plots a spectrum as annotated in a sparky .save file

Usage
-----

python plot_sparky.py spc.save spc.ucsf outfile xlim_d xlim_u ylim_d ylim_u

where *_d and *_u indicate downlfield and upfield limits, respectively.

"""



def plot(dic, data, outfile=None, xlims=[], ylims=[]):
    """
    Plot the sparky data as it was annotated in the save file

    """

    # get ppm scale, and adjust using the shifts given in .save file
    udic = ng.sparky.guess_udic(dic, data)
    uc = {i: ng.fileiobase.uc_from_udic(udic, i) for i in range(2)}
    n15 = [i + dic["spectrum"]["shift"][0] for i in uc[0].ppm_limits()]
    h1 = [i + dic["spectrum"]["shift"][1] for i in uc[1].ppm_limits()]
    ex = [*h1, *n15]


    # adjust contour levels, the ones in .save file is a good start
    c = dic["view"][0]["contour_pos"]
    clev = [c[1] * 1.2 * c[2] ** i for i in range(7)]


    # plot limits
    if xlims == []:
        xlims = uc[1].ppm_limits()
    if ylims == []:
        ylims = uc[0].ppm_limits()


    # plot
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100, constrained_layout=True)

    # plot contours and label axes
    ax.contour(data, extent=ex, levels=clev, colors="k", linewidths=0.5)
    ax.set_xlim(*xlims)
    ax.set_ylim(*ylims)
    for pos in "xy":
        ax.tick_params(axis=pos, labelsize=14)
    ax.set_xlabel(r"$\mathrm{^1H\ (ppm)}$", fontsize=15)
    ax.set_ylabel(r"$\mathrm{^{15}N\ (ppm)}$", fontsize=15)


    # put in labels and peak positions
    for k, v in dic["ornament"].items():
        label_loc = v["xy"][1]
        label = v["label"][0].split("N_")[0]
        peak_loc = v["pos"][::-1]

        # annotate only if the peak is present in limits of the current window
        if (xlims[1] < peak_loc[0] < xlims[0]) and (
            ylims[1] < peak_loc[1] < ylims[0]
        ):

            ax.scatter(*peak_loc, marker="x", c="k", s=20)
            ax.annotate(
                s=label,
                xy=peak_loc,
                xytext=label_loc,
                size=12,
                ha="center",
                va="center",
                arrowprops=dict(
                    arrowstyle="wedge, tail_width=0.1",
                    fc="0",
                    ec="none",
                    connectionstyle="arc3, rad=-0.1",
                ),
            )

    # save figure
    if outfile is None:
        outfile = "plot"
    fig.savefig(f"{outfile}.png")

    return


if __name__ == "__main__":

    from sys import argv
    import nmrglue as ng
    import matplotlib.pyplot as plt
    plt.style.use("ggplot")

    savefile = argv[1]
    spectrum_file = argv[2]
    outfile = argv[3]

    xlims = [float(i) for i in argv[4:6]]
    ylims = [float(i) for i in argv[6:8]]

    # read a sparky savefile (.save) and the corresponding spectrum (.ucsf)
    dic, data = ng.sparky.read_savefile(
        savefile=savefile, spectrum_file=spectrum_file,
    )

    plot(dic, data, outfile, xlims, ylims)
