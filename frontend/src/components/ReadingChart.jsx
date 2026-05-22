import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

function ReadingChart({ readings, anomalies }) {
  const anomalyTimes = new Set(anomalies.map((anomaly) => anomaly.timestamp));
  const labels = readings.map((reading) => reading.time);
  const values = readings.map((reading) => reading.temperature);

  const pointColors = readings.map((reading) => {
    if (anomalyTimes.has(reading.timestamp)) {
      return reading.temperature > 60 ? '#dc2626' : '#2563eb';
    }
    return '#15803d';
  });

  const data = {
    labels,
    datasets: [
      {
        label: 'Temperature C',
        data: values,
        borderColor: '#334155',
        backgroundColor: '#334155',
        pointBackgroundColor: pointColors,
        pointBorderColor: pointColors,
        pointRadius: readings.length > 80 ? 2 : 4,
        tension: 0.25,
      },
      {
        label: 'Minimum valid',
        data: labels.map(() => -50),
        borderColor: '#2563eb',
        borderDash: [6, 5],
        pointRadius: 0,
      },
      {
        label: 'Maximum valid',
        data: labels.map(() => 60),
        borderColor: '#dc2626',
        borderDash: [6, 5],
        pointRadius: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.parsed.y.toFixed(2)} C`,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          maxTicksLimit: 8,
        },
      },
      y: {
        title: {
          display: true,
          text: 'Celsius',
        },
      },
    },
  };

  return (
    <div className="chart-panel">
      <h3>Reading trend</h3>
      <div className="chart-frame">
        <Line data={data} options={options} />
      </div>
    </div>
  );
}

export default ReadingChart;
