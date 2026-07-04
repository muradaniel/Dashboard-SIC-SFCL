# Harmonic Signal Examples

Generic synthetic 60 Hz signals in the same column structure used by the COMSOL TXT exports read by the dashboard. They are only waveform examples, not design combinations.

## Column Order

```text
H (cm)  W (cm)  N_DC  N_AC  Time (s)  Corrente de Curto (A)  Queda de Tensao (V)
```

Lines starting with `%` are comments and are ignored by the dashboard readers.

## Files

- `sinal_60hz_senoidal.txt`: pure sinusoidal waveform.
- `sinal_60hz_quadrado.txt`: square waveform.
- `sinal_60hz_triangular.txt`: triangular waveform.
- `sinal_60hz_trapezio.txt`: trapezoidal waveform.
- `sinal_60hz_dente_de_serra.txt`: sawtooth waveform.
- `sinal_60hz_retificado.txt`: full-wave rectified sinusoidal waveform.
- `sinal_60hz_com_harmonicos_3_5_7.txt`: sinusoidal waveform with 3rd, 5th and 7th harmonics.

## Signal Setup

- Fundamental frequency: 60 Hz.
- Duration: 1.0 s.
- Sampling frequency: 20 kHz.
- Points per file: 20000.
- Current scale: +/- 10 A, except rectified signal from 0 to 10 A.
- Voltage scale: +/- 20 V, except rectified signal from 0 to 20 V.
- Geometry/winding parameters: set to 0 because these files are literally just arbitrary signals, not COMSOL design combinations.