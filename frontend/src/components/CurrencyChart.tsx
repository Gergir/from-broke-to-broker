import {Line} from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

interface Rate {
    update_date: string;
    mid: number;
}

interface Props {
    rates: Rate[];
    periodType: 'day' | 'month' | 'quarter' | 'year';
}

const CurrencyChart = ({rates}: Props) => {
    const data = {
        labels: rates.map(rate => rate.update_date),
        datasets: [
            {
                label: 'Exchange Rate',
                data: rates.map(rate => rate.mid),
                borderColor: 'rgb(79, 70, 229)',
                backgroundColor: 'rgba(79, 70, 229, 0.2)',
                tension: 0.1,
                fill: true,
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: true,
                text: 'Exchange Rate History',
            },
        },
        scales: {
            y: {
                beginAtZero: false,
                title: {
                    display: true,
                    text: 'PLN Value'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Date'
                },
                reverse: true,
            }
        },
    };

    return <Line data={data} options={options}/>;
};

export default CurrencyChart;