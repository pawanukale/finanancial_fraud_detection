import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Alert, Spin, DatePicker } from 'antd';
import { 
  DollarOutlined, 
  AlertOutlined, 
  TransactionOutlined, 
  LineChartOutlined 
} from '@ant-design/icons';
import axios from 'axios';
import './App.css';

const { RangePicker } = DatePicker;

const columns = [
  {
    title: 'Transaction ID',
    dataIndex: 'transaction_id',
    key: 'transaction_id',
  },
  {
    title: 'Amount',
    dataIndex: 'amount',
    key: 'amount',
    render: amount => `$${amount.toFixed(2)}`,
  },
  {
    title: 'User',
    dataIndex: 'user_id',
    key: 'user_id',
  },
  {
    title: 'Fraud Probability',
    dataIndex: 'fraud_probability',
    key: 'fraud_probability',
    render: prob => (
      <span style={{ color: prob > 0.85 ? 'red' : prob > 0.7 ? 'orange' : 'green' }}>
        {(prob * 100).toFixed(1)}%
      </span>
    ),
  },
  {
    title: 'Time',
    dataIndex: 'timestamp',
    key: 'timestamp',
    render: ts => new Date(ts).toLocaleString(),
  },
];

function App() {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState({
    stats: true,
    alerts: true,
    trends: true
  });
  const [dateRange, setDateRange] = useState([7]);

  useEffect(() => {
    // Fetch dashboard data
    const fetchData = async () => {
      try {
        setLoading(prev => ({ ...prev, stats: true }));
        const statsRes = await axios.get('http://localhost:5000/api/stats');
        setStats(statsRes.data);
        
        setLoading(prev => ({ ...prev, alerts: true }));
        const alertsRes = await axios.get('http://localhost:5000/api/alerts');
        setAlerts(alertsRes.data.alerts);
        
        setLoading(prev => ({ ...prev, trends: true }));
        const trendsRes = await axios.get('http://localhost:5000/api/trends', {
          params: { days: dateRange[0] }
        });
        setTrends(trendsRes.data.trends);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading({ stats: false, alerts: false, trends: false });
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [dateRange]);

  return (
    <div className="dashboard">
      <h1>Fraud Detection Dashboard</h1>
      
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card loading={loading.stats}>
            <StatCard 
              icon={<TransactionOutlined />}
              title="Total Transactions"
              value={stats?.stats.total_count || 0}
              color="#1890ff"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading.stats}>
            <StatCard 
              icon={<AlertOutlined />}
              title="Fraudulent Transactions"
              value={stats?.stats.fraud_count || 0}
              color="#f5222d"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading.stats}>
            <StatCard 
              icon={<DollarOutlined />}
              title="Total Amount"
              value={stats?.stats.total_amount?.toFixed(2) || '0.00'}
              prefix="$"
              color="#52c41a"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading.stats}>
            <StatCard 
              icon={<LineChartOutlined />}
              title="Fraud Rate"
              value={(stats?.fraud_rate * 100)?.toFixed(2) || '0.00'}
              suffix="%"
              color="#faad14"
            />
          </Card>
        </Col>
      </Row>
      
      <Row gutter={16}>
        <Col span={16}>
          <Card 
            title="Fraud Trends" 
            extra={
              <RangePicker 
                onChange={(dates, dateStrings) => setDateRange([dates[1].diff(dates[0], 'days')])}
              />
            }
            loading={loading.trends}
          >
            <TrendChart data={trends} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Recent Fraud Alerts" loading={loading.alerts}>
            <AlertList alerts={alerts} />
          </Card>
        </Col>
      </Row>
      
      <Row style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="Transaction Details" loading={loading.alerts}>
            <Table 
              columns={columns} 
              dataSource={alerts} 
              rowKey="transaction_id"
              pagination={{ pageSize: 5 }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

const StatCard = ({ icon, title, value, prefix = '', suffix = '', color }) => (
  <div className="stat-card">
    <div className="stat-icon" style={{ backgroundColor: color }}>{icon}</div>
    <div className="stat-content">
      <div className="stat-title">{title}</div>
      <div className="stat-value">
        {prefix}{value}{suffix}
      </div>
    </div>
  </div>
);

const TrendChart = ({ data }) => {
  // Implement with your preferred charting library (e.g., Chart.js, ECharts)
  return <div className="trend-chart">Chart visualization would go here</div>;
};

const AlertList = ({ alerts }) => (
  <div className="alert-list">
    {alerts.slice(0, 5).map(alert => (
      <Alert
        key={alert.transaction_id}
        message={`Transaction ${alert.transaction_id}`}
        description={`$${alert.amount.toFixed(2)} - ${(alert.fraud_probability * 100).toFixed(1)}% risk`}
        type="error"
        showIcon
        style={{ marginBottom: 8 }}
      />
    ))}
  </div>
);

export default App;