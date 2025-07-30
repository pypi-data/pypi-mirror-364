import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import AutoMinorLocator
import numpy as np
from numpy.typing import ArrayLike, NDArray
import itertools
import pathlib

from . import utils as ut


def gaussian(p: ArrayLike, fwhm: float, b: float, area: float) -> NDArray:
    """
    Gaussian g(p) with given peak position (b), fwhm, and area

    g(p) = area/(c*sqrt(2pi)) * exp(-(p-b)**2/(2c**2))

    c = fwhm/(2*np.sqrt(2*np.log(2)))

    Parameters
    ----------
    p : array_like
        Continuous variable
    fwhm: float
        Full Width at Half-Maximum
    b : float
        Peak position
    area : float
        Area of Gaussian function

    Return
    ------
    list[float]
        g(p) at each value of p
    """

    c = fwhm / (2 * np.sqrt(2 * np.log(2)))

    a = 1. / (c * np.sqrt(2 * np.pi))

    gaus = a * np.exp(-(p - b)**2 / (2 * c**2))

    gaus *= area

    return gaus


def lorentzian(p: ArrayLike, fwhm, p0, area) -> NDArray:
    """
    Lotenztian L(p) with given peak position (b), fwhm, and area

    L(p) = (0.5*area*fwhm/pi) * 1/((p-p0)**2 + (0.5*fwhm)**2)

    Parameters
    ----------
    p : array_like
        Continuous variable
    fwhm: float
        Full Width at Half-Maximum
    p0 : float
        Peak position
    area : float
        Area of Lorentzian function

    Return
    ------
    list[float]
        L(p) at each value of p
    """

    lor = 0.5 * fwhm / np.pi
    lor *= 1. / ((p - p0)**2 + (0.5 * fwhm)**2)

    lor *= area

    return lor


def plot_abs(x_values: ArrayLike, x_type: str, foscs: ArrayLike,
             lineshape: str = 'gaussian', linewidth: float = 100.,
             x_lim: list[float] = ['auto', 'auto'],
             abs_type: str = 'napierian',
             y_lim: list[float] = [0., 'auto'],
             x_shift: float = 0., normalise: bool = False,
             osc_style: str = 'separate', save: bool = False,
             save_name: str = 'absorption_spectrum.png', show: bool = False,
             verbose: bool = True,
             window_title: str = 'Absorption Spectrum',
             plot_type: str = 'absorption') -> tuple[plt.Figure, list[plt.Axes]]: # noqa
    '''
    Plots absorption spectrum with intensity specified by oscillator strength.\n # noqa
    Spectrum is computed as a sum of Gaussian or Lorentzian lineshapes.\n
    The x_values can be either wavenumbers [cm^-1], wavelengths [nm] or\n
    energies [eV].\n

    Parameters
    ----------
    x_values: array_like
        x_values for each transition, either wavenumber, wavelength or energy\n
        with unit type specified by x_type
    x_type: str {'wavenumber', 'wavelength', 'energy'}
        Type of x_values, either wavenumber [cm^-1], wavelength [nm] or\n
        energy [eV].
    foscs: array_like
        Oscillator strength of each transition
    lineshape: str {'gaussian', 'lorentzian'}
        Lineshape function to use for each transition/signal
    linewidth: float
        Linewidth used in lineshape [cm^-1]
    x_lim: list[float], default ['auto', 'auto']
        Minimum and maximum x-values to plot [cm^-1 or nm]
    y_lim: list[float | str], default [0., 'auto']
        Minimum and maximum y-values to plot [cm^-1 mol^-1 L]
    abs_type: str {'napierian', 'logarithmic'}
        Absorbance (and epsilon) type to use. Orca_mapspc uses napierian
    normalise: bool, default False
        If True, normalise the absorption spectrum to the maximum value.
    osc_style: str, default 'separate'
        Style of oscillator strength plots:
        - 'separate': plots oscillator strengths as stems on separate axis
        - 'combined': plots oscillator strengths on intensity axis
        - 'off': does not plot oscillator strengths
    save: bool, default False
        If True, plot is saved to save_name
    save_name: str | pathlib.Path, default 'absorption_spectrum.png'
        If save is True, plot is saved to this location/filename
    show: bool, default False
        If True, plot is shown on screen
    verbose: bool, default True
        If True, plot file location is written to terminal
    window_title: str, default 'UV-Visible Absorption Spectrum'
        Title of figure window, not of plot
    plot_type: str, default 'absorption'
        Type of plot to create, either 'absorption' or 'emission'.

    Returns
    -------
    plt.Figure
        Matplotlib Figure object
    list[plt.Axes]
        Matplotlib Axis object for main plot followed by\n
        Matplotlib Axis object for twinx oscillator strength axis
    '''

    save_name = pathlib.Path(save_name)

    x_values = np.asarray(x_values) + x_shift
    foscs = np.asarray(foscs)
    if len(x_values) != len(foscs):
        raise ValueError('x_values and foscs must have the same length')

    fig, ax = plt.subplots(1, 1, num=window_title)

    ls_func = {
        'gaussian': gaussian,
        'lorentzian': lorentzian
    }

    if not isinstance(x_lim, list):
        raise ValueError('`x_lim` must be a list of values')

    if x_lim[0] != x_lim[1]:
        if isinstance(x_lim[0], str):
            if x_lim[0] == 'auto':
                x_lim[0] = ax.get_ylim()[0]
            else:
                x_lim[0] = float(x_lim[0])
        if isinstance(x_lim[1], str):
            if x_lim[1] == 'auto':
                x_lim[1] = ax.get_ylim()[1]
            else:
                x_lim[1] = float(x_lim[1])
    else:
        x_lim = [np.min(x_values), np.max(x_values)]

    # Set limits and range of continuous variable
    ax.set_xlim([x_lim[0], x_lim[1]])
    x_grid = np.linspace(x_lim[0], x_lim[1], 100000)

    # Exclude values of x_values out of the range of x_lim
    x_values = np.asarray(
        [val for val in x_values if x_lim[0] <= val <= x_lim[1]]
    )
    # Exclude oscillator strengths for those values
    foscs = np.asarray(
        [
            fosc
            for val, fosc in zip(x_values, foscs)
            if x_lim[0] <= val <= x_lim[1]]
    )

    # Conversion from oscillator strength to napierian integrated absorption
    # coefficient
    # This is the value of A for a harmonically oscillating electron
    A_elec = 2.31E8
    # convert to common log absorbance if desired
    if abs_type == 'log':
        A_elec /= np.log(10)
    A_logs = [fosc * A_elec for fosc in foscs]

    # Spectrum as sum of signals. Always computed in wavenumbers.
    spectrum = np.sum([
        ls_func[lineshape](x_grid, linewidth, x_value, A_log)
        for x_value, A_log in zip(x_values, A_logs)
    ], axis=0)

    if normalise:
        # Normalise the spectrum to the maximum value
        spectrum /= np.max(spectrum)
        ax.set_ylabel(
            'Normalised {} (arbitrary units)'.format(
                plot_type.capitalize()
            )
        )  # noqa
    else:
        ax.set_ylabel(r'$\epsilon$ (cm$^\mathregular{-1}$ mol$^\mathregular{-1}$ L)') # noqa

    _txt_save_name = save_name.with_suffix('.txt')
    np.savetxt(
        _txt_save_name,
        np.vstack([x_grid, spectrum]).T,
        fmt='%.5f',
        header=f'{plot_type.capitalize()} spectrum data\nx (wavenumber, wavelength or energy), y (absorbance)' # noqa
    )
    if verbose:
        ut.cprint(
            f'\n{plot_type.capitalize()} spectrum data saved to\n {_txt_save_name}', # noqa
            'cyan'
        )

    # Main spectrum
    ax.plot(x_grid, spectrum, color='k')

    if osc_style == 'separate':
        fax = ax.twinx()
        # Oscillator strength twin axis
        fax.stem(x_values, foscs, basefmt=' ', markerfmt=' ')
        fax.yaxis.set_minor_locator(AutoMinorLocator())
        fax.set_ylabel(r'$f_\mathregular{osc}$')
        fax.set_ylim([0., fax.get_ylim()[1]])
    elif osc_style == 'combined':
        fax = None
        plt.subplots_adjust(right=0.2)
        ax.stem(
            x_values,
            foscs/np.max(foscs) * np.max(spectrum),
            basefmt=' ',
            markerfmt=' '
        )
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
    else:
        fax = None
        # No oscillator strength plot
        plt.subplots_adjust(right=0.2)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

    if y_lim[0] != y_lim[1]:
        if isinstance(y_lim[0], str):
            if y_lim[0] == 'auto':
                y_lim[0] = ax.get_ylim()[0]
            else:
                y_lim[0] = float(y_lim[0])
        if isinstance(y_lim[1], str):
            if y_lim[1] == 'auto':
                y_lim[1] = ax.get_ylim()[1]
            else:
                y_lim[1] = float(y_lim[1])
        ax.set_ylim([y_lim[0], y_lim[1]])

    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    xtype_to_label = {
        'wavenumber': r'Wavenumber (cm$^\mathregular{-1}$)',
        'wavelength': 'Wavelength (nm)',
        'energy': r'Energy (eV)'
    }

    ax.set_xlabel(xtype_to_label[x_type.lower()])

    fig.tight_layout()

    if save:
        plt.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(
                f'\n{plot_type.capitalize()} spectrum saved to\n {save_name}',
                'cyan'
            )

    if show:
        plt.show()

    return fig, [ax, fax]


def wl_to_wn(wl: float) -> float:
    if wl == 0:
        return 0.
    else:
        return 1E7 / wl


def plot_chit(chit: ArrayLike, temps: ArrayLike, fields: ArrayLike = None,
              y_unit: str = r'cm^3\,K\,mol^{-1}', # noqa
              save: bool = False, save_name: str = 'chit_vs_t.png',
              show: bool = False, window_title: str = 'Calculated Susceptibility') -> tuple[plt.Figure, plt.Axes]: # noqa
    r'''
    Plots susceptibility*T data as a function of temperature

    Parameters
    ----------
    chit: array_like
        Susceptibility * Temperature
    temps: array_like
        Temperatures in Kelvin
    fields: array_like, optional
        If specified, splits data according to applied magnetic field.\n
        One plot, with one trace per field.
    y_unit: str, default 'cm^3\ K\ mol^{-1}'
        Mathmode y-unit which matches input chit data
    save: bool, default False
        If True, plot is saved to save_name
    save_name: str, default 'chit_vs_t.png'
        If save is True, plot is saved to this location/filename
    show: bool, default False
        If True, plot is shown on screen
    window_title: str, default 'Calculated Susceptibility'
        Title of figure window, not of plot
    Returns
    -------
    plt.Figure
        Matplotlib Figure object
    plt.Axes
        Matplotlib Axis object for plot
    ''' # noqa

    # Create figure and axes
    fig, ax = plt.subplots(1, 1, figsize=(5, 4), num=window_title)

    if fields is None:
        # Plot data as it is
        ax.plot(temps, chit, color='k', label='Calculated')
    else:
        # Split data by field
        ufields = np.unique(fields)

        for ufield in ufields:
            _temp = temps[fields == ufield]
            _chit = chit[fields == ufield]
            ax.plot(
                _temp,
                _chit,
                label=f'Calculated ($H$ = {ufield:.1f} Oe)'
            )
        ax.legend(frameon=False)

    ax.set_xlabel('$T$ (K)')
    ax.set_ylabel(rf'$\chi T\,\mathregular{{({y_unit})}}$')

    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    fig.tight_layout()

    if save:
        plt.savefig(save_name, dpi=500)

    if show:
        plt.show()

    return fig, ax


def plot_ir(wavenumbers: ArrayLike, linear_absorbance: ArrayLike,
            lineshape: str = 'lorentzian', linewidth: float = 10.,
            x_lim: list[float] = [None, None],
            save: bool = False, save_name: str = 'ir.png', show: bool = False,
            window_title: str = 'Infrared spectrum'):
    '''
    Plots Infrared Spectrum

    Parameters
    ----------
    wavenumbers: array_like
        Wavenumbers of each transition [cm^-1]
    linear_absorbance: array_like
        Absorbance of each transition
    lineshape: str {'gaussian', 'lorentzian'}
        Lineshape function to use for each transition/signal
    linewidth: float
        Linewidth used in lineshape [cm^-1]
    x_lim: list[float], default [None, None]
        Minimum and maximum x-values to plot [cm^-1]
    save: bool, default False
        If True, plot is saved to save_name
    save_name: str
        If save is True, plot is saved to this location/filename
    show: bool, default False
        If True, plot is shown on screen
    window_title: str, default 'Infrared Spectrum'
        Title of figure window, not of plot
    '''

    fig, ax = plt.subplots(1, 1, num=window_title)

    ls_func = {
        'gaussian': gaussian,
        'lorentzian': lorentzian
    }

    if None not in x_lim:
        x_range = np.linspace(x_lim[0], x_lim[1], 100000)
    else:
        x_range = np.linspace(0, np.max(wavenumbers) * 1.1, 100000)

    # Spectrum as sum of signals. Always computed in wavenumbers.
    spectrum = np.sum([
        ls_func[lineshape](x_range, linewidth, wavenumber, a)
        for wavenumber, a in zip(wavenumbers, linear_absorbance)
    ], axis=0)

    np.savetxt('spectrum.txt', np.vstack([x_range, spectrum]).T, fmt='%.5f')

    # Main spectrum
    ax.plot(x_range, spectrum, color='k')

    ax.set_xlim([0, np.max(x_range)])

    plt.subplots_adjust(right=0.2)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    ax.set_xlabel(r'Wavenumber (cm$^\mathregular{-1}$)')
    ax.set_ylabel(r'$\epsilon$ (cm$^\mathregular{-1}$ mol$^\mathregular{-1}$ L)') # noqa

    fig.tight_layout()

    if save:
        plt.savefig(save_name, dpi=500)

    if show:
        plt.show()

    return fig, ax


def plot_raman(wavenumbers: ArrayLike, intensities: ArrayLike,
               lineshape: str = 'gaussian', linewidth: float = 10.,
               x_lim: list[float] = 0., x_unit: str = 'wavenumber',
               abs_type: str = 'absorption', y_lim: list[float] = 'auto',
               save: bool = False, save_name: str = 'raman.png',
               show: bool = False,
               window_title: str = 'Raman spectrum'):
    '''
    Plots Raman Spectrum
    '''

    raise NotImplementedError


def plot_cd(save: bool = False, save_name: str = 'raman.png',
            show: bool = False,
            window_title: str = 'Raman spectrum'):
    '''
    Plots circular dichroism data
    '''

    raise NotImplementedError


def plot_ailft_orb_energies(energies: ArrayLike, labels: ArrayLike = None,
                            groups: ArrayLike = None,
                            occupations: ArrayLike = None,
                            y_unit: str = r'cm^{-1}',
                            save: bool = False,
                            save_name: str = 'ai_lft_energies.png',
                            show: bool = False,
                            window_title: str = 'AI-LFT Orbital Energies',
                            verbose: bool = True) -> tuple[plt.Figure, plt.Axes]: # noqa
    '''
    Parameters
    ----------
    energies: array_like
        Energies which are in same unit as y_unit
    labels: array_like | None, optional
        If provided, labels are added next to energy levels.
    groups: array_like | None, optional
        If provided, groups orbitals together by offsetting x coordinate
    occupations: array_like | None, optional
        If provided, each orbital is populated with either 0, 1 or 2 electrons
    y_unit: str, default 'cm^{-1}'
        Mathmode y-unit which matches input chit data
    save: bool, default False
        If True, plot is saved to save_name
    save_name: str, default 'ai_lft_energies.png'
        If save is True, plot is saved to this location/filename
    show: bool, default False
        If True, plot is shown on screen
    window_title: str, default 'AI-LFT Orbital Energies'
        Title of figure window, not of plot
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib Figure object
    plt.Axes
        Matplotlib Axis object for plot
    '''

    fig, ax = plt.subplots(1, 1, figsize=(3.5, 3.5), num=window_title)
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    if groups is not None:
        groups = list(groups)
        groups = ut.flatten_recursive(groups)
        if len(groups) != len(energies):
            raise ValueError('Number of groups does not match number of states') # noqa
        # Split group by differing value
        groups = [list(x) for _, x in itertools.groupby(groups)]
        # X values for each group
        xvals = [list(range(len(grp))) for grp in groups]
        # Centre each group so that the middle is zero
        xvals = [g - sum(grp)/len(grp) for grp in xvals for g in grp]
    else:
        xvals = [1] * len(energies)

    ax.plot(
        xvals,
        energies,
        lw=0,
        marker='_',
        mew=1.5,
        color='k',
        markersize=25
    )

    if occupations is not None:
        if len(occupations) != len(energies):
            raise ValueError('Number of occupation numbers does not match number of states') # noqa

        # Make spin up and spin down arrow markers
        spup = mpl.markers.MarkerStyle(marker=r'$\leftharpoondown$')
        spup._transform = spup.get_transform().rotate_deg(-90)

        spdown = mpl.markers.MarkerStyle(marker=r'$\leftharpoondown$')
        spdown._transform = spdown.get_transform().rotate_deg(90)

        # Plot each marker
        for occ, en, xval in zip(occupations, energies, xvals):
            lx = xval - 1 / 10
            rx = xval + 1 / 10
            # Up and down
            if occ == 2:
                ax.scatter(lx, en, s=400, marker=spup, color='k', linewidths=0.001) # noqa
                ax.scatter(rx, en, s=400, marker=spdown, color='k', lw=0.001)
            # up
            elif occ == 1:
                ax.scatter(lx, en, s=400, marker=spup, color='k', lw=0.001)
            # down
            elif occ == -1:
                ax.scatter(rx, en, s=400, marker=spdown, color='k', lw=0.001)

    if labels is not None:
        for xval, energy, label in zip(xvals, energies, labels):
            ax.text(
                xval * 1.05,
                energy,
                rf'${label}$'
            )

    ax.set_xticklabels([])
    ax.set_xticks([])
    _lims = ax.get_xlim()
    if groups is None:
        ax.set_xlim([_lims[0]*0.9, _lims[1]*1.2])
    else:
        ax.set_xlim([_lims[0]*1.2, _lims[1]*1.2])

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.set_ylabel(rf'Energy $\mathregular{{({y_unit})}}$')

    fig.tight_layout()

    if save:
        plt.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(f'\nAI-LFT orbitals saved to\n{save_name}', 'cyan')

    if show:
        plt.show()
