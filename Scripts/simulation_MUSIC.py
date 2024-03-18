from DSP import recorders, filters, direction_of_arrival, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    samplerate = 44100
    blocksize = 1024
    frequencies = (675, 500)
    doas = (10, 30)
    spacing = 0.254
    snr = 50
    channels = 6

    app = QtWidgets.QApplication([])

    # Components
    plotter = plotters.SingleLinePlotter(
        title='MUSIC Spectrum',
        x_label='Angle (Deg)',
        y_label='Music',
        x_range=(-90, 90),
        y_range=(0, 1),
        interval=int(1000 * blocksize / samplerate)
    )
    music = direction_of_arrival.MUSIC((plotter.in_queue,), spacing=0.5, num_mics=channels, num_sources=2)
    hanning = filters.HanningWindow((music.in_queue,))
    fir = filters.FIRWINFilter((hanning.in_queue,), N=100, cutoff=1200, type='filtfilt')
    recorder = recorders.AudioSimulator(
        destinations=(fir.in_queue, ),
        frequencies=frequencies,
        doas=doas,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=channels,
        blocksize=blocksize,
        sleep=False
    )

    recorder.start()
    fir.start()
    hanning.start()
    music.start()
    plotter.show()
    app.exec()


if __name__ == '__main__':
    main()
