import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import { format } from 'date-fns';
import 'react-datepicker/dist/react-datepicker.css';

interface DateSelectorProps {
  periodType: string;
  setPeriodType: (type: string) => void;
  dateValue: string;
  setDateValue: (value: string) => void;
}

const CustomInput: React.FC<{ value: string; onClick: () => void }> = ({ value, onClick }) => (
  <input
    className="date-input"
    value={value}
    onClick={onClick}
    readOnly
    placeholder="Select date"
  />
);

const DateSelector: React.FC<DateSelectorProps> = ({
  periodType,
  setPeriodType,
  dateValue,
  setDateValue,
}) => {
  const [internalDate, setInternalDate] = useState<Date>(new Date(dateValue));

  useEffect(() => {
    setInternalDate(new Date(dateValue));
  }, [dateValue]);

  const handleDateChange = (date: Date) => {
    let formattedDate = '';
    switch (periodType) {
      case 'year':
        formattedDate = format(date, 'yyyy');
        break;
      case 'quarter':
        const quarter = Math.ceil((date.getMonth() + 1) / 3);
        formattedDate = `${format(date, 'yyyy')}-Q${quarter}`;
        break;
      case 'month':
        formattedDate = format(date, 'yyyy-MM');
        break;
      default:
        formattedDate = format(date, 'yyyy-MM-dd');
    }
    setDateValue(formattedDate);
  };

  return (
    <div className="date-selector">
      <select
        value={periodType}
        onChange={(e) => setPeriodType(e.target.value)}
        className="period-select"
      >
        <option value="day">Daily</option>
        <option value="month">Monthly</option>
        <option value="quarter">Quarterly</option>
        <option value="year">Yearly</option>
      </select>

      <div className="date-picker-container">
        {periodType === 'year' && (
          <DatePicker
            selected={internalDate}
            onChange={handleDateChange}
            dateFormat="yyyy"
            showYearPicker
            customInput={<CustomInput value={dateValue} onClick={() => {}} />}
          />
        )}

        {periodType === 'quarter' && (
          <DatePicker
            selected={internalDate}
            onChange={handleDateChange}
            dateFormat="yyyy-QQQ"
            showQuarterYearPicker
            customInput={<CustomInput value={dateValue} onClick={() => {}} />}
          />
        )}

        {periodType === 'month' && (
          <DatePicker
            selected={internalDate}
            onChange={handleDateChange}
            dateFormat="yyyy-MM"
            showMonthYearPicker
            customInput={<CustomInput value={dateValue} onClick={() => {}} />}
          />
        )}

        {periodType === 'day' && (
          <DatePicker
            selected={internalDate}
            onChange={handleDateChange}
            dateFormat="yyyy-MM-dd"
            customInput={<CustomInput value={dateValue} onClick={() => {}} />}
          />
        )}
      </div>
    </div>
  );
};

export default DateSelector;
