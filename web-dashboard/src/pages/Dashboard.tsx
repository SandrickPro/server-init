import {
    CheckCircle as CheckIcon,
    CloudQueue as CloudIcon,
    Error as ErrorIcon,
    Memory as MemoryIcon,
    Refresh as RefreshIcon,
    Security as SecurityIcon,
    Speed as SpeedIcon,
    Storage as StorageIcon,
    Timeline as TimelineIcon,
    Warning as WarningIcon,
} from '@mui/icons-material';
import {
    Box,
    Card,
    CardContent,
    Chip,
    Grid,
    IconButton,
    LinearProgress,
    Paper,
    Typography,
} from '@mui/material';
import axios from 'axios';
import {
    CategoryScale,
    Chart as ChartJS,
    Filler,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Title,
    Tooltip,
} from 'chart.js';
import { motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import toast from 'react-hot-toast';
import { useQuery } from 'react-query';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  timestamp: string;
}

interface ServiceStatus {
  name: string;
  status: 'running' | 'stopped' | 'error';
  uptime: number;
  cpu: number;
  memory: number;
}

const Dashboard: React.FC = () => {
  const [metricsHistory, setMetricsHistory] = useState<SystemMetrics[]>([]);

  // Fetch system metrics
  const { data: metrics, refetch: refetchMetrics } = useQuery<SystemMetrics>(
    'metrics',
    async () => {
      const response = await axios.get('/api/metrics/current');
      return response.data;
    },
    {
      refetchInterval: 5000, // Refresh every 5 seconds
      onError: () => {
        toast.error('Failed to fetch system metrics');
      },
    }
  );

  // Fetch service status
  const { data: services } = useQuery<ServiceStatus[]>(
    'services',
    async () => {
      const response = await axios.get('/api/services/status');
      return response.data;
    },
    {
      refetchInterval: 10000,
    }
  );

  // Update metrics history
  useEffect(() => {
    if (metrics) {
      setMetricsHistory((prev) => {
        const newHistory = [...prev, metrics];
        // Keep only last 20 data points
        return newHistory.slice(-20);
      });
    }
  }, [metrics]);

  // Chart configuration
  const chartData = {
    labels: metricsHistory.map((m) => new Date(m.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'CPU %',
        data: metricsHistory.map((m) => m.cpu),
        borderColor: '#00ff41',
        backgroundColor: 'rgba(0, 255, 65, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Memory %',
        data: metricsHistory.map((m) => m.memory),
        borderColor: '#00d4ff',
        backgroundColor: 'rgba(0, 212, 255, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'default';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckIcon />;
      case 'stopped':
        return <WarningIcon />;
      case 'error':
        return <ErrorIcon />;
      default:
        return null;
    }
  };

  const MetricCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
  }> = ({ title, value, icon, color }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        sx={{
          background: 'linear-gradient(135deg, #1a1f3a 0%, #2a3050 100%)',
          border: `1px solid ${color}`,
          height: '100%',
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6" color="textSecondary">
              {title}
            </Typography>
            <Box sx={{ color }}>{icon}</Box>
          </Box>
          <Typography variant="h3" fontWeight="bold" color={color} gutterBottom>
            {value.toFixed(1)}%
          </Typography>
          <LinearProgress
            variant="determinate"
            value={value}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(255,255,255,0.1)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: color,
              },
            }}
          />
          {value > 80 && (
            <Chip
              label="High Usage"
              size="small"
              sx={{ mt: 1 }}
              color={value > 90 ? 'error' : 'warning'}
            />
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" color="primary" gutterBottom>
            🚀 DevOps Platform Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Real-time system monitoring and management
          </Typography>
        </Box>
        <IconButton onClick={() => refetchMetrics()} color="primary">
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Metric Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="CPU Usage"
            value={metrics?.cpu || 0}
            icon={<SpeedIcon fontSize="large" />}
            color="#00ff41"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Memory Usage"
            value={metrics?.memory || 0}
            icon={<MemoryIcon fontSize="large" />}
            color="#00d4ff"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Disk Usage"
            value={metrics?.disk || 0}
            icon={<StorageIcon fontSize="large" />}
            color="#ff4444"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Network I/O"
            value={metrics?.network || 0}
            icon={<CloudIcon fontSize="large" />}
            color="#ffaa00"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <TimelineIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Performance Trends</Typography>
            </Box>
            <Box height="calc(100% - 50px)">
              <Line data={chartData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, height: 400, overflow: 'auto' }}>
            <Box display="flex" alignItems="center" mb={2}>
              <SecurityIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Service Status</Typography>
            </Box>
            {services?.map((service, index) => (
              <motion.div
                key={service.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Box
                  sx={{
                    p: 2,
                    mb: 1,
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: 2,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {service.name}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Uptime: {Math.floor(service.uptime / 60)}h {service.uptime % 60}m
                    </Typography>
                  </Box>
                  <Chip
                    icon={getStatusIcon(service.status)}
                    label={service.status}
                    color={getStatusColor(service.status)}
                    size="small"
                  />
                </Box>
              </motion.div>
            ))}
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item>
            <Chip
              label="Deploy"
              color="primary"
              onClick={() => toast.success('Opening deployment wizard...')}
            />
          </Grid>
          <Grid item>
            <Chip
              label="Scale Up"
              color="secondary"
              onClick={() => toast.success('Scaling resources...')}
            />
          </Grid>
          <Grid item>
            <Chip
              label="Backup Now"
              onClick={() => toast.success('Starting backup...')}
            />
          </Grid>
          <Grid item>
            <Chip
              label="Security Scan"
              color="error"
              onClick={() => toast.success('Running security scan...')}
            />
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default Dashboard;
