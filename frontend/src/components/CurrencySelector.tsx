const CurrencySelector = ({ currencies, selectedCurrency, setSelectedCurrency }) => (
  <select
    value={selectedCurrency}
    onChange={(e) => setSelectedCurrency(e.target.value)}
  >
    <option value="">All Currencies</option>
    {currencies.map(currency => (
      <option key={currency.code} value={currency.code}>
        {currency.currency} ({currency.code})
      </option>
    ))}
  </select>
);

export default CurrencySelector;
