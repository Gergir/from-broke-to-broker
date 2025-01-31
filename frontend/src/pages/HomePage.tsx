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
    const [lastFetchType, setLastFetchType] = useState<'table' | 'rate' | null>(null);

    useEffect(() => {
        const checkBackend = async () => {
            try {
                await axios.get('/currencies/', {timeout: 2000});
                setBackendAvailable(true);
                await fetchCurrencies();
            } catch (error) {
                    const message = error.response.data?.detail || error.response.data?.message || error.message;

                if (message === 'No currencies found. Try to fetch them first.') {
                    setBackendAvailable(true);
                } else {
                    setBackendAvailable(false);
                    setError('Backend service unavailable - please start the API server');
                }
            }
        };

        checkBackend();
    }, []);


    const fetchCurrencies = async () => {
        try {
            const response = await axios.get('/currencies/');
            setCurrencies(response.data);

            if (response.data.length === 0) {
                setError('No currencies available. Please initialize rates first.');
            } else {
                setError(''); // Clear error if currencies are available
            }
        } catch (err) {
            handleError(err, err.message);
        }
    };

    const handleError = (error: unknown, defaultMessage: string) => {
        setRates([]);
        if (axios.isAxiosError(error)) {
            setError(error.response?.data?.detail || error.message || defaultMessage);
        } else {
            setError(defaultMessage);
        }
    };

    const initializeRates = async () => {
        setLoading(true);
        setError('');
        try {
            await axios.post('/currencies/fetch/tables');
            setLastFetchType('table');
            await Promise.all([fetchCurrencies(), getRates()]);
        } catch (err) {
            handleError(err, 'Failed to initialize rates');
        } finally {
            setLoading(false);
        }
    };

    const getRates = async () => {
        setLoading(true);
        setError('');
        try {
            let requestDate = '';
            const currentDate = new Date(dateValue);

            switch (periodType) {
                case 'year':
                    requestDate = format(currentDate, 'yyyy');
                    break;
                case 'quarter':
                    requestDate = `${format(currentDate, 'yyyy')}-Q${Math.ceil((currentDate.getMonth() + 1) / 3)}`;
                    break;
                case 'month':
                    requestDate = format(currentDate, 'yyyy-MM');
                    break;
                default:
                    requestDate = format(currentDate, 'yyyy-MM-dd');
            }

            const response = await axios.get(`/currencies/${requestDate}`, {
                params: {code: selectedCurrency || undefined}
            });

            const sortedRates = response.data.sort((a: Rate, b: Rate) =>
                new Date(b.update_date).getTime() - new Date(a.update_date).getTime()
            );
            setRates(sortedRates);
        } catch (err) {
            handleError(err, 'Failed to fetch rates');
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

            setLastFetchType(selectedCurrency ? 'rate' : 'table');
            await getRates();
        } catch (err) {
            handleError(err, 'Failed to fetch rates');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <h1>Currency Rates</h1>

            {!backendAvailable && (
                <div className="error" style={{color: 'red', fontWeight: 'bold'}}>
                    Backend connection failed! Make sure the API server is running on port 8000
                </div>
            )}


            {!rates.length && !error && currencies.length === 0 && backendAvailable && (
                <div className="empty-state">
                    <button onClick={initializeRates} className="init-button">
                        Initialize Rates
                    </button>
                </div>
            )}

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

                <button onClick={getRates} disabled={loading || !backendAvailable}>
                    {loading ? 'Loading...' : 'Show Rates'}
                </button>

                <button onClick={fetchRates} disabled={loading || !backendAvailable}>
                    {loading ? 'Fetching...' : 'Fetch Rates'}
                </button>
            </div>

            {error && (
                <div className="error">
                    <strong>Error:</strong> {error}
                    {lastFetchType && (
                        <button
                            className="error-retry"
                            onClick={lastFetchType === 'table' ? initializeRates : getRates}
                        >
                            Try Again
                        </button>
                    )}
                </div>
            )}

            {rates.length > 0 ? (
                <RatesTable rates={rates}/>
            ) : (
                !error && <div className="empty-state">No rates found for selected period</div>
            )}

            {loading && <div className="loading">Loading data...</div>}
        </div>
    );
};

export default HomePage;