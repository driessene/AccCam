import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wavenumber = 12.3
    speed_of_sound = 343

    # Sphere
    elements = [doa.Element(np.array([-1.25, 0, 0]), samplerate),
                doa.Element(np.array([-0.75, 0, 0]), samplerate),
                doa.Element(np.array([-0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.75, 0, 0]), samplerate),
                doa.Element(np.array([1.25, 0, 0]), samplerate),
                doa.Element(np.array([0, -1.25, 0]), samplerate),
                doa.Element(np.array([0, -0.75, 0]), samplerate),
                doa.Element(np.array([0, -0.25, 0]), samplerate),
                doa.Element(np.array([0, 0.25, 0]), samplerate),
                doa.Element(np.array([0, 0.75, 0]), samplerate),
                doa.Element(np.array([0, 1.25, 0]), samplerate),
                doa.Element(np.array([0, 0, 0.25]), samplerate),
                doa.Element(np.array([0, 0, 0.75]), samplerate),
                doa.Element(np.array([0, 0, 1.25]), samplerate)]

    structure = doa.Structure(
        elements=elements,
        wavenumber=wavenumber,
        snr=50,
        blocksize=blocksize,
        inclination_resolution=100,
        azimuth_resolution=100
    )
    structure.visualize()

    wavevectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 0.98, 1, 1])), speed_of_sound),
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 1.02, 2, 2])), speed_of_sound),
    ]

    # Get hz for debugging
    for wavevector in wavevectors:
        print(wavevector.linear_frequency)

    # Recorder to get data
    recorder = dsp.AudioSimulator(
        structure=structure,
        wavevectors=wavevectors
    )

    # Filter
    filt = dsp.FirlsFilter(
        n=1001,
        num_channels=len(elements),
        bands=np.array([0, 399.99, 400, 800, 800.01, samplerate/2]),
        desired=np.array([0, 0, 1, 1, 0, 0]),
        samplerate=samplerate,
        method='filtfilt',
        normalize=True,
        remove_offset=True
    )
    filt.plot_response()
    filt.plot_coefficients()

    # MUSIC
    estimator = doa.MVDRBeamformer(structure)

    music = dsp.DOAEstimator(estimator)

    # Plot
    plot = dsp.HeatmapPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=structure.inclination_values,
        y_data=structure.azimuths_values,
        interval=blocksize/samplerate,
        cmap='inferno'
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(music, 0)
    music.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    music.start()
    plot.start()
    plot.show()


if __name__ == '__main__':
    main()
