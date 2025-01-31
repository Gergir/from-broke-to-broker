interface RatesTableProps {
  rates: Array<{
    update_date: string;
    currency: string;
    code: string;
    mid: number;
  }>;
}

const RatesTable = ({ rates }: RatesTableProps) => {
  if (!rates.length) return null;

  return (
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Currency</th>
          <th>Code</th>
          <th>Rate</th>
        </tr>
      </thead>
      <tbody>
        {rates.map(rate => (
          <tr key={`${rate.update_date}-${rate.code}`}>
            <td>{new Date(rate.update_date).toLocaleDateString()}</td>
            <td>{rate.currency}</td>
            <td>{rate.code}</td>
            <td>{rate.mid.toFixed(4)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default RatesTable;