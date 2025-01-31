import React, {useEffect, useState} from 'react';
import DatePicker from 'react-datepicker';
import {format, startOfQuarter} from 'date-fns';
import 'react-datepicker/dist/react-datepicker.css';

interface DateSelectorProps {
    dateValue: string;
    setDateValue: (value: string) => void;
    periodType: 'day' | 'month' | 'quarter' | 'year';
    setPeriodType: (type: 'day' | 'month' | 'quarter' | 'year') => void;
}

const DateSelector: React.FC<DateSelectorProps> = ({
    dateValue,
    setDateValue,
    periodType,
    setPeriodType
}) => {
    const [selectedDate, setSelectedDate] = useState<Date>(new Date(dateValue));

    useEffect(() => {
        setSelectedDate(new Date(dateValue));
    }, [dateValue]);

    const handleDateChange = (date: Date) => {
        let formattedDate = '';
        switch (periodType) {
            case 'year':
                formattedDate = format(date, 'yyyy');
                break;
            case 'quarter':
                const quarterStart = startOfQuarter(date);
                formattedDate = format(quarterStart, 'yyyy-MM-dd');
                break;
            case 'month':
                formattedDate = format(date, 'yyyy-MM');
                break;
            case 'day':
            default:
                formattedDate = format(date, 'yyyy-MM-dd');
        }
        setDateValue(formattedDate);
    };

    return (
        <div className="date-selector">
            <div className="period-buttons">
                {(['day', 'month', 'quarter', 'year'] as const).map((type) => (
                    <button
                        key={type}
                        className={`period-button ${periodType === type ? 'active' : ''}`}
                        onClick={() => setPeriodType(type)}
                    >
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                ))}
            </div>

            <DatePicker
                selected={selectedDate}
                onChange={handleDateChange}
                inline
                calendarClassName="custom-calendar"
                showMonthYearPicker={periodType === 'month'}
                showQuarterYearPicker={periodType === 'quarter'}
                showYearPicker={periodType === 'year'}
                dateFormat={
                    periodType === 'year' ? 'yyyy' :
                    periodType === 'quarter' ? 'yyyy-QQQ' :
                    periodType === 'month' ? 'MM/yyyy' : 
                    'dd/MM/yyyy'
                }
            />

            <div className="selected-period">
                Selected {periodType}: {formatSelectedPeriod(selectedDate, periodType)}
            </div>
        </div>
    );
};

const formatSelectedPeriod = (date: Date, periodType: string) => {
    switch (periodType) {
        case 'year':
            return format(date, 'yyyy');
        case 'quarter':
            const quarter = Math.ceil((date.getMonth() + 1) / 3);
            return `${format(date, 'yyyy')}-Q${quarter}`;
        case 'month':
            return format(date, 'yyyy-MM');
        default:
            return format(date, 'yyyy-MM-dd');
    }
};

export default DateSelector;