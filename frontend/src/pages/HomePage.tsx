import {useEffect, useState} from 'react';
import axios from 'axios';
import DateSelector from '../components/DateSelector';
import CurrencySelector from '../components/CurrencySelector';
import RatesTable from '../components/RatesTable';
import {endOfMonth, endOfQuarter, endOfYear, format, parseISO} from 'date-fns';


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

const today = new Date();
const HomePage = () => {
    const [dateValue, setDateValue] = useState(format(new Date(), 'yyyy-MM-dd'));
    const [periodType, setPeriodType] = useState<'day' | 'month' | 'quarter' | 'year'>('day');
    const [currencies, setCurrencies] = useState<Currency[]>([]);
    const [selectedCurrency, setSelectedCurrency] = useState('');
    const [rates, setRates] = useState<Rate[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [backendAvailable, setBackendAvailable] = useState(true);
    const [hasInitialized, setHasInitialized] = useState(false);
    const [showRates, setShowRates] = useState(false);

    useEffect(() => {
        const checkBackend = async () => {
            try {
                await axios.get('/currencies/');
                setBackendAvailable(true);
                fetchCurrencies();
            } catch (error: any) {
                if (error.response?.status === 404) {
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
        } catch (err) {
            handleError(err, 'Failed to fetch currencies');
        }
    };

    const handleError = (error: any, defaultMessage: string) => {
        setRates([]);
        setShowRates(false);
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
            setHasInitialized(true);
            await fetchCurrencies();
        } catch (err) {
            handleError(err, 'Failed to initialize rates. Please check backend connection.');
        } finally {
            setLoading(false);
        }
    };

    const getRates = async () => {
        setLoading(true);
        setError('');
        try {
            let requestDate = '';
            const date = parseISO(dateValue);

            switch (periodType) {
                case 'year':
                    requestDate = format(date, 'yyyy');
                    break;
                case 'quarter':
                    const quarter = Math.ceil((date.getMonth() + 1) / 3);
                    requestDate = `${format(date, 'yyyy')}-Q${quarter}`;
                    break;
                case 'month':
                    requestDate = format(date, 'yyyy-MM');
                    break;
                case 'day':
                default:
                    requestDate = format(date, 'yyyy-MM-dd');
            }

            const response = await axios.get(`/currencies/${requestDate}`, {
                params: {code: selectedCurrency || undefined}
            });

            setRates(response.data.sort((a: Rate, b: Rate) =>
                new Date(b.update_date).getTime() - new Date(a.update_date).getTime()
            ));
            setShowRates(true);
        } catch (err) {
            handleError(err, 'Failed to fetch rates. Please try again.');
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
                    if (endOfYear(dateFrom) > today && dateFrom < today) {
                        dateTo = today;
                    } else {
                        dateTo = endOfYear(dateFrom);
                    }
                    break;
                case 'quarter':
                    if (endOfQuarter(dateFrom) > today && dateFrom < today) {
                        dateTo = today;
                    } else {
                        dateTo = endOfQuarter(dateFrom);

                    }

                    break;
                case 'month':
                    if (endOfMonth(dateFrom) > today && dateFrom < today) {
                        dateTo = today;
                    } else {
                        dateTo = endOfMonth(dateFrom);
                    }

                    break;
                case 'day':
                    dateTo = dateFrom;
                    break;
            }

             if (selectedCurrency) {
            await axios.post('/currencies/fetch/rates', null, {
                params: {
                    code: selectedCurrency,
                    date_from: format(dateFrom, 'yyyy-MM-dd'),
                    date_to: format(dateTo, 'yyyy-MM-dd'),
                }
            });
        } else {
            await axios.post('/currencies/fetch/tables', null, {
                params: {
                    date_from: format(dateFrom, 'yyyy-MM-dd'),
                    date_to: format(dateTo, 'yyyy-MM-dd'),
                }
            });
        }

            await getRates();
        } catch (err) {
            handleError(err, 'Failed to fetch rates');
        } finally {
            setLoading(false);
        }
    };

    const showInitButton = currencies.length === 0 && !hasInitialized;

    return (
        <div className="container">
            <h1>Currency Rates</h1>

            {!backendAvailable && (
                <div className="error" style={{color: 'red', fontWeight: 'bold'}}>
                    Backend connection failed! Make sure the API server is running on port 8000
                </div>
            )}

            {showInitButton && (
                <div className="empty-state">
                    <button onClick={initializeRates} className="init-button" disabled={loading}>
                        {loading ? 'Initializing...' : 'Initialize Rates'}
                    </button>
                </div>
            )}

            {!showInitButton && (
                <div className="controls">
                    <DateSelector
                        dateValue={dateValue}
                        setDateValue={setDateValue}
                        periodType={periodType}
                        setPeriodType={setPeriodType}
                    />

                    <CurrencySelector
                        currencies={currencies}
                        selectedCurrency={selectedCurrency}
                        setSelectedCurrency={setSelectedCurrency}
                    />

                    <div className="action-buttons">
                        <button onClick={getRates} disabled={loading}>
                            {loading ? 'Loading...' : 'Show Rates'}
                        </button>
                        <button onClick={fetchRates} disabled={loading}>
                            {loading ? 'Fetching...' : 'Fetch Rates'}
                        </button>
                    </div>
                </div>
            )}

            {loading && <div className="loading">Loading data...</div>}

            {showRates && rates.length > 0 ? (
                <RatesTable rates={rates}/>
            ) : (
                showRates && <div className="empty-state">No rates found for selected period</div>
            )}

            {error && (
                <div className="error">
                    {error}
                </div>
            )}
        </div>
    );
};

export default HomePage;