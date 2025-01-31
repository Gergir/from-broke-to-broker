import React from "react";
import { format, parseISO } from 'date-fns';

const DateSelector = ({ periodType, setPeriodType, dateValue, setDateValue }) => {
  const handlePeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPeriodType(e.target.value);
    setDateValue(format(new Date(), 'yyyy-MM-dd'));
  };

  const getDateInputType = () => {
    switch (periodType) {
      case 'year': return 'year';
      case 'quarter': return 'month';
      case 'month': return 'month';
      default: return 'date';
    }
  };

  return (
    <div className="date-selector">
      <select value={periodType} onChange={handlePeriodChange}>
        <option value="day">Daily</option>
        <option value="month">Monthly</option>
        <option value="quarter">Quarterly</option>
        <option value="year">Yearly</option>
      </select>

      <input
        type={getDateInputType()}
        value={dateValue}
        onChange={(e) => setDateValue(e.target.value)}
      />
    </div>
  );
};

export default DateSelector;