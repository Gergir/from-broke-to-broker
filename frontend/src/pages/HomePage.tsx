import {useState, useEffect} from 'react';
import axios from 'axios';
import DateSelector from '../components/DateSelector';
import CurrencySelector from '../components/CurrencySelector';
import RatesTable from '../components/RatesTable';
import {
    format,
    parseISO,
    startOfYear,
    endOfYear,
    startOfQuarter,
    endOfQuarter,
    startOfMonth,
    endOfMonth
} from 'date-fns';

interface Rate {
    update_date: string;
    currency: string;
    code: string;
    mid: number;
}

interface Currency {
    currency: string;
    code: string;
}


const HomePage = () => {
    const [periodType, setPeriodType] = useState('day');
    const [dateValue, setDateValue] = useState(format(new Date(), 'yyyy-MM-dd'));
    const [currencies, setCurrencies] = useState<Currency[]>([]);
    const [selectedCurrency, setSelectedCurrency] = useState('');
    const [rates, setRates] = useState<Rate[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [backendAvailable, setBackendAvailable] = useState(true);

    useEffect(() => {
        const checkBackend = async () => {
            try {
                await axios.get('/currencies/', {timeout: 2000});
                setBackendAvailable(true);
            } catch (error) {
                setBackendAvailable(false);
                setError('Backend service unavailable - please start the API server');
            }
        };

        checkBackend();
        fetchCurrencies();
    }, []);

    useEffect(() => {
        console.log('Component mounted')
        fetchCurrencies()
    }, [])

    useEffect(() => {
        console.log('Currencies updated:', currencies)
    }, [currencies])

    useEffect(() => {
        console.log('Rates updated:', rates)
    }, [rates])

    const fetchCurrencies = async () => {
        try {
            const response = await axios.get('/currencies/');
            setCurrencies(response.data);
        } catch (err) {
            setError('Failed to fetch currencies');
        }
    };

    const getRates = async () => {
        setLoading(true);
        setError('');
        try {
            let requestDate = '';
            const today = new Date();

            switch (periodType) {
                case 'year':
                    requestDate = format(parseISO(dateValue), 'yyyy');
                    break;
                case 'quarter':
                    requestDate = `${format(parseISO(dateValue), 'yyyy')}-Q${Math.ceil((parseISO(dateValue).getMonth() + 1) / 3)}`;
                    break;
                case 'month':
                    requestDate = format(parseISO(dateValue), 'yyyy-MM');
                    break;
                default:
                    requestDate = format(parseISO(dateValue), 'yyyy-MM-dd');
            }

            const response = await axios.get(`/currencies/${requestDate}`, {
                params: {code: selectedCurrency || undefined}
            });

            setRates(response.data);
        } catch (err) {
            setError('Failed to fetch rates. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const fetchRates = async () => {
        setLoading(true);
        setError('');
        try {
            const dateFrom = parseISO(dateValue);
            let dateTo = parseISO(dateValue);

            switch (periodType) {
                case 'year':
                    dateTo = endOfYear(dateFrom);
                    break;
                case 'quarter':
                    dateTo = endOfQuarter(dateFrom);
                    break;
                case 'month':
                    dateTo = endOfMonth(dateFrom);
                    break;
            }

            const endpoint = selectedCurrency ? '/currencies/fetch/rates' : '/currencies/fetch/tables';
            await axios.post(endpoint, null, {
                params: {
                    code: selectedCurrency,
                    date_from: format(dateFrom, 'yyyy-MM-dd'),
                    date_to: format(dateTo, 'yyyy-MM-dd')
                }
            });

            await getRates(); // Refresh rates after fetch
        } catch (err) {
            setError('Failed to fetch rates. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (

        <div>
            <h1>Currency Rates</h1>

            <div className="controls">
                <DateSelector
                    periodType={periodType}
                    setPeriodType={setPeriodType}
                    dateValue={dateValue}
                    setDateValue={setDateValue}
                />

                <CurrencySelector
                    currencies={currencies}
                    selectedCurrency={selectedCurrency}
                    setSelectedCurrency={setSelectedCurrency}
                />

                <button onClick={getRates} disabled={loading}>
                    {loading ? 'Loading...' : 'Show Rates'}
                </button>

                <button onClick={fetchRates} disabled={loading}>
                    {loading ? 'Fetching...' : 'Fetch Rates'}
                </button>
            </div>

            {error && <div className="error">{error}</div>}

            <RatesTable rates={rates}/>

            {!backendAvailable &&
                <div className="error">Backend service unavailable - please start the API server</div>}

        </div>


    );
};

export default HomePage;