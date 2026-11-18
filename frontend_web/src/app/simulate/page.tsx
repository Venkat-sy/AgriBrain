"use client";
import React, { useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Button,
  Badge,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Label,
  Alert,
  AlertTitle,
  AlertDescription,
  Table,
  TableHeader,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableCaption,
  Separator,
  ScrollArea,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui";
import {
  MapPin,
  ArrowLeft,
  AlertCircle,
  CloudRain,
  Cpu,
  Calendar,
  Droplets,
  Sun,
  Leaf,
  Sparkles,
  TrendingUp,
  TrendingDown,
  Minus,
  Plus,
  CheckCircle,
  XCircle,
  Info,
  Loader2,
  Target,
  BarChart3,
  Zap,
  Shield,
  Search,
  ChevronDown,
  ChevronUp,
  MoreHorizontal,
  Download,
  RefreshCw,
  Settings,
  Eye,
  EyeOff,
  Copy,
  Share2,
  Printer,
  FileText,
  Image,
  Mail,
  Bell,
  Flag,
  Star,
  Heart,
  Bookmark,
  Tag,
  Filter,
  X,
  Maximize,
  Minimize,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Home,
  Menu,
  LogOut,
  User,
  Lock,
  Unlock,
  Key,
  Database,
  Server,
  Globe,
  Wifi,
  WifiOff,
  Signal,
  Battery,
  BatteryLow,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  Camera,
  CameraOff,
  Send,
  Paperclip,
  Link2,
  ExternalLink,
  Anchor,
  BookOpen,
  GraduationCap,
  Award,
  Medal,
  Trophy,
  Crown,
  Gem,
  Diamond,
  Circle,
  Square,
  Triangle,
  Hexagon,
  Octagon,
  Pentagon,
  Star as StarIcon,
  Heart as HeartIcon,
  Zap as ZapIcon,
  Shield as ShieldIcon,
  Check,
  X as XIcon,
  Minus as MinusIcon,
  Plus as PlusIcon,
  ArrowUp,
  ArrowDown,
  ArrowLeft as ArrowLeftIcon,
  ArrowRight,
  ArrowUpRight,
  ArrowDownRight,
  ArrowDownLeft,
  ArrowUpLeft,
  CornerUpLeft,
  CornerUpRight,
  CornerDownLeft,
  CornerDownRight,
  Move,
  RotateCw,
  FlipHorizontal,
  FlipVertical,
  Crop,
  ZoomIn,
  ZoomOut,
    Maximize2,
    Minimize2,
    Fullscreen,
    PanelLeft,
    PanelRight,
    PanelTop,
    PanelBottom,
    Sidebar,
    Layout,
    Grid,
    List,
    Columns,
    Rows,
    SplitSquareHorizontal,
    SplitSquareVertical,
    Tractor,
    Package,
    IndianRupee,
    Brain,
  } from "lucide-react";

const MapUI = dynamic(() => import("@/components/MapUI"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[320px] sm:h-[390px] lg:h-[430px] rounded-2xl bg-slate-900 animate-pulse flex items-center justify-center text-slate-400 border border-slate-800">
      Loading Interactive India Map...
    </div>
  ),
});

import { ApiService } from "@/services/api";

// 8 Standard Indian Soil Profiles for User Confirmation & Override
const SOIL_PROFILES: Record<string, { N: number; P: number; K: number; pH: number; desc: string }> = {
  "Indo-Gangetic Alluvial": { N: 215, P: 58, K: 155, pH: 7.1, desc: "Fertile riverine silt; ideal for cereals, pulses & sugarcane" },
  "Deccan Black Cotton (Regur)": { N: 160, P: 48, K: 185, pH: 7.4, desc: "High clay moisture retention; ideal for cotton, soybean, citrus" },
  "Coastal Lateritic / Alluvial": { N: 150, P: 38, K: 165, pH: 5.7, desc: "Acidic, well-drained coastal soil; ideal for paddy, coconut, arecanut" },
  "Southern Red Loam": { N: 145, P: 42, K: 135, pH: 6.4, desc: "Porous friable loam; ideal for millets, groundnut, mango, pulses" },
  "Arid Sandy / Calcareous": { N: 95, P: 28, K: 115, pH: 7.9, desc: "Low organic matter, fast draining; suitable for bajra, mustard, pomegranate" },
  "Mountain Forest / Podzolic": { N: 185, P: 52, K: 150, pH: 6.0, desc: "Humus-rich temperate soil; ideal for apple, spices, potato" },
  "Deltaic Clay Loam": { N: 195, P: 54, K: 170, pH: 6.6, desc: "Moisture-retentive delta soil; high yield for rice, jute, banana" },
  "Saline / Alkaline Usar": { N: 110, P: 32, K: 125, pH: 8.2, desc: "High salt profile; requires gypsum & salt-tolerant varieties" },
  };

  interface MetricCardProps {
    label: string;
    value: string;
    icon: React.ReactNode;
  }

  function MetricCard({ label, value, icon }: MetricCardProps) {
    return (
      <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">{icon}</div>
          <div>
            <p className="text-xs text-slate-500 font-medium">{label}</p>
            <p className="text-lg font-bold text-slate-900">{value}</p>
          </div>
        </div>
      </div>
    );
  }

  export default function SimulatePage() {
  const router = useRouter();
  const [pin, setPin] = useState<{ lat: number; lng: number } | null>({ lat: 12.9716, lng: 77.5946 });
  const [manualLat, setManualLat] = useState<string>('12.9716');
  const [manualLng, setManualLng] = useState<string>('77.5946');
  const [districtName, setDistrictName] = useState<string>('Bengaluru Urban, Karnataka');
  const [agroZone, setAgroZone] = useState<string>('Central & Southern Deccan Plateau');

  const [selectedSoilType, setSelectedSoilType] = useState<string>('Southern Red Loam');
  const [soilConfirmed, setSoilConfirmed] = useState<boolean>(true);
  const [areaAcres, setAreaAcres] = useState<number>(3.0);
  const [setupType, setSetupType] = useState<'seasonal' | 'perennial'>('seasonal');

  const [useOverrides, setUseOverrides] = useState<boolean>(false);
  const [overrides, setOverrides] = useState({ rainfall: 115, temp: 27, humidity: 64, ph: 6.4, N: 145, P: 42, K: 135 });

  const [loading, setLoading] = useState<boolean>(false);
  const [statusBanner, setStatusBanner] = useState<string | null>(null);
  const [data, setData] = useState<any | null>(null);
  const [selectedCropIndex, setSelectedCropIndex] = useState<number>(0);

  // Auto-detect regional zone & default soil from coordinates
  const inferRegionalProfile = (lat: number, lon: number) => {
    const isHimalayan = lat > 29.8;
    const isCoastal = (lon < 76.2 && lat < 19.5) || (lon > 79.8 && lat < 21.0);
    const isNorthern = lat > 25.5 && lon > 74.5;
    const isArid = lon < 74.5 && lat > 22.0;
    const isDeccanBlack = lat >= 16.5 && lat <= 23.5 && lon >= 73.5 && lon <= 79.5;

    let detectedSoil = 'Southern Red Loam';
    let zone = 'Southern Plateau & Hills Zone';
    let rain = 120;
    let temp = 27.5;
    let hum = 65;

    if (isHimalayan) {
      detectedSoil = 'Mountain Forest / Podzolic';
      zone = 'Western Himalayan Temperate Zone';
      rain = Math.round(145 + (lon * 3) % 60);
      temp = Number((16.5 + (lon % 4)).toFixed(1));
      hum = 68;
    } else if (isCoastal) {
      detectedSoil = 'Coastal Lateritic / Alluvial';
      zone = 'Coastal Alluvial & Lateritic Monsoon Zone';
      rain = Math.round(240 + (lat * 5) % 90);
      temp = Number((28.5 + (lat % 3)).toFixed(1));
      hum = 82;
    } else if (isNorthern) {
      detectedSoil = 'Indo-Gangetic Alluvial';
      zone = 'Indo-Gangetic Plains Zone';
      rain = Math.round(105 + (lon * 3) % 55);
      temp = Number((24.5 + (lon % 5)).toFixed(1));
      hum = 60;
    } else if (isArid) {
      detectedSoil = 'Arid Sandy / Calcareous';
      zone = 'Western Arid & Thar Zone';
      rain = Math.round(48 + (lat * 2) % 35);
      temp = Number((32.5 + (lat % 3.5)).toFixed(1));
      hum = 38;
    } else if (isDeccanBlack) {
      detectedSoil = 'Deccan Black Cotton (Regur)';
      zone = 'Central Deccan Plateau Zone';
      rain = Math.round(110 + (lat * 3) % 65);
      temp = Number((29.0 + (lon % 3.5)).toFixed(1));
      hum = 56;
    }

    const sp = SOIL_PROFILES[detectedSoil];
    return { detectedSoil, zone, rain, temp, hum, sp };
  };

  const handlePinDrop = async (lat: number, lng: number) => {
      const cleanLat = Number(lat.toFixed(4));
      const cleanLng = Number(lng.toFixed(4));
      setPin({ lat: cleanLat, lng: cleanLng });
      setManualLat(String(cleanLat));
      setManualLng(String(cleanLng));
      setStatusBanner(null);

      // Get spatial data from backend
      try {
        const spatialResult = await ApiService.lookupDistrict(cleanLat, cleanLng);
        setSelectedSoilType(spatialResult?.soil_type || "Southern Red Loam");
        setAgroZone(spatialResult?.agro_zone || "Central & Southern Deccan Plateau");
        setDistrictName(spatialResult?.district || `${cleanLat}°N, ${cleanLng}°E`);
        setOverrides({
          rainfall: spatialResult?.weather?.rainfall || 100,
          temp: spatialResult?.weather?.temp || 27,
          humidity: spatialResult?.weather?.humidity || 65,
          ph: spatialResult?.soil?.pH || 6.5,
          N: spatialResult?.soil?.N || 150,
          P: spatialResult?.soil?.P || 40,
          K: spatialResult?.soil?.K || 150,
        });
      } catch {
        // Fallback to basic values
        setDistrictName(`${cleanLat}°N, ${cleanLng}°E`);
      }
    };

  const handleSoilTypeChange = (newSoil: string) => {
      setSelectedSoilType(newSoil);
    };

    const applyManualCoordinates = () => {
      const parsedLat = parseFloat(manualLat);
      const parsedLng = parseFloat(manualLng);
      if (!isNaN(parsedLat) && !isNaN(parsedLng) && parsedLat >= 6 && parsedLat <= 38 && parsedLng >= 68 && parsedLng <= 98) {
        handlePinDrop(parsedLat, parsedLng);
      } else {
        setStatusBanner('Please enter valid Indian coordinates (Lat: 6° to 38°N, Lng: 68° to 98°E).');
      }
    };

    // Run simulation via backend API
    const runSimulation = async () => {
      if (!pin) return;
      setLoading(true);
      setStatusBanner(null);

      try {
        // First get district info from spatial lookup
        const spatialResult = await ApiService.lookupDistrict(pin.lat, pin.lng);
        const districtId = spatialResult?.district_id || 1;
      
        // Determine planting season based on setup type and month
        const currentMonth = new Date().getMonth() + 1;
        let plantingSeason = "Kharif";
                if (setupType === "perennial") {
                  plantingSeason = "Perennial";
        } else if (currentMonth >= 6 && currentMonth <= 10) {
          plantingSeason = "Kharif";
        } else if (currentMonth >= 11 || currentMonth <= 2) {
          plantingSeason = "Rabi";
        } else {
          plantingSeason = "Zaid";
        }

        const result = await ApiService.runSimulation({
          district_id: districtId,
          selected_crop: data?.ranked_crops?.[0]?.name || data?.recommended_crop || "Rice (Paddy)",
          land_area_ha: areaAcres / 2.471, // Convert acres to hectares
          budget_inr: 100000, // Default budget
          confirmed_soil_type: selectedSoilType,
          rainfall_override_mm: useOverrides ? overrides.rainfall : 0,
          planting_season: plantingSeason,
          planned_start_date: new Date().toISOString().split('T')[0],
        });

        // Validate response before changing the rendered results.
        if (!result || typeof result !== 'object') {
          throw new Error('Simulation returned an invalid response');
        }
        const rankedCrops = Array.isArray(result.ranked_crops)
          ? result.ranked_crops
          : Array.isArray(result.alternatives)
            ? result.alternatives
            : [];
        const payload = {
          district: result.district ?? null,
          agro_zone: result.agro_zone ?? null,
          area_acres: areaAcres,
          setup_type: setupType,
          weather: result.weather ?? null,
          soil: result.soil ?? null,
          rainfall_forecast: Array.isArray(result.rainfall_forecast) ? result.rainfall_forecast : [],
          ranked_crops: rankedCrops,
          recommended_crop: result.recommended_crop ?? null,
          timeline: Array.isArray(result.timeline) ? result.timeline : [],
        };

        setSelectedCropIndex(0);
        setData(payload);
        try {
          localStorage.setItem('agribrain_last_simulation', JSON.stringify(payload));
        } catch (storageError) {
          console.warn('Unable to cache simulation results:', storageError);
        }
        setLoading(false);
      } catch (error) {
        console.error('Simulation error:', error);
        setStatusBanner('Failed to run simulation. Please try again.');
        setLoading(false);
      }
    };

    const activeCrop = data?.ranked_crops?.[selectedCropIndex] || null;

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">AgriBrain Simulate</h1>
              <p className="text-xs text-slate-500">Digital Twin Crop Suitability Engine</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Engine Active
            </Badge>
            <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")}>
              <ArrowLeft className="w-4 h-4 mr-1" />
              Dashboard
            </Button>
          </div>
        </div>
      </header>

      {/* Status Banner */}
      {statusBanner && (
        <div className="max-w-7xl mx-auto px-4 py-2 animate-slide-down">
                <Alert variant="destructive" className="mb-0 rounded-none border-x-0 border-t-0 border-b-0">
                  <AlertCircle className="w-4 h-4" />
                  <AlertTitle className="text-sm">Simulation notice</AlertTitle>
                  <AlertDescription className="text-xs">{statusBanner}</AlertDescription>
                </Alert>
              </div>
            )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Loading Overlay */}
        {loading && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-slate-600">Running digital twin inference...</p>
              <p className="text-xs text-slate-400 mt-1">Scoring 45 crops with SHAP explainability</p>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-[1fr_420px] gap-6">
          {/* Left Panel - Map & Inputs */}
          <div className="space-y-6">
            {/* Map Section */}
            <Card className="overflow-hidden">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-lg">Farm Location & Agro-Zone</CardTitle>
                <Badge variant={pin ? "default" : "secondary"} className="text-xs">
                  {pin ? "Pinned" : "Click Map to Pin"}
                </Badge>
              </CardHeader>
              <CardContent className="p-0">
                <MapUI
                  center={[pin?.lat || 20.5937, pin?.lng || 78.9629]}
                  zoom={pin ? 7 : 5}
                  pin={pin}
                  onPinDrop={handlePinDrop}
                  className="h-[380px] w-full"
                />
              </CardContent>
            </Card>

            {/* Detected Region Info */}
            {pin && (
              <Card className="border-emerald-200 bg-emerald-50">
                <CardContent className="pt-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <p className="text-xs text-slate-500">District</p>
                      <p className="font-semibold text-slate-900">{districtName}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Agro-Zone</p>
                      <p className="font-semibold text-slate-900">{agroZone}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Soil Profile</p>
                      <p className="font-semibold text-slate-900 text-emerald-700">{selectedSoilType}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Coordinates</p>
                      <p className="font-mono text-xs text-slate-700">{pin.lat.toFixed(4)}, {pin.lng.toFixed(4)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Input Controls */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Simulation Parameters
                </CardTitle>
                <CardDescription>Configure farm setup, area, and environmental overrides</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Setup Type & Area */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium">Farm Setup Type</Label>
                    <Select value={setupType} onValueChange={(v: string) => setSetupType(v as 'seasonal' | 'perennial')}>
                                          <SelectTrigger className="mt-1"><SelectValue placeholder="Select setup" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="seasonal">Seasonal Crops (25 varieties)</SelectItem>
                        <SelectItem value="perennial">Perennial Crops (20 varieties)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Farm Area (Acres)</Label>
                    <Input type="number" min="0.1" max="1000" step="0.1" value={areaAcres} onChange={(e) => setAreaAcres(Number(e.target.value))} className="mt-1" />
                  </div>
                </div>

                {/* Soil Type */}
                <div>
                  <Label className="text-sm font-medium">Confirmed Soil Profile</Label>
                  <Select value={selectedSoilType} onValueChange={setSelectedSoilType}>
                                        <SelectTrigger className="mt-1 w-full md:w-1/2"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {Object.entries(SOIL_PROFILES).map(([key, v]) => (
                        <SelectItem key={key} value={key}>
                          <div className="flex flex-col">
                            <span className="font-medium">{key}</span>
                            <span className="text-xs text-slate-500">pH: {v.pH} | N:{v.N} P:{v.P} K:{v.K} kg/ha</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Overrides Toggle */}
                <div className="flex items-center justify-between border-t pt-4">
                  <div>
                    <Label className="font-medium flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={useOverrides}
                        onChange={(e) => setUseOverrides(e.target.checked)}
                        className="w-4 h-4 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500"
                      />
                      Enable Environmental Overrides
                    </Label>
                    <p className="text-xs text-slate-500 mt-1">Manually adjust weather & soil nutrients for scenario testing</p>
                  </div>
                </div>

                {/* Override Inputs */}
                {useOverrides && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t pt-4 animate-fade-in">
                    <div>
                      <Label className="text-sm">Temp (°C)</Label>
                      <Input type="number" step="0.5" min="5" max="45" value={overrides.temp} onChange={(e) => setOverrides({...overrides, temp: Number(e.target.value)})} className="mt-1" />
                    </div>
                    <div>
                      <Label className="text-sm">Humidity (%)</Label>
                      <Input type="number" min="10" max="100" value={overrides.humidity} onChange={(e) => setOverrides({...overrides, humidity: Number(e.target.value)})} className="mt-1" />
                    </div>
                    <div>
                      <Label className="text-sm">Rainfall (mm)</Label>
                      <Input type="number" min="0" max="3000" value={overrides.rainfall} onChange={(e) => setOverrides({...overrides, rainfall: Number(e.target.value)})} className="mt-1" />
                    </div>
                    <div>
                      <Label className="text-sm">Soil pH</Label>
                      <Input type="number" step="0.1" min="4" max="9" value={overrides.ph} onChange={(e) => setOverrides({...overrides, ph: Number(e.target.value)})} className="mt-1" />
                    </div>
                    <div>
                      <Label className="text-sm">Nitrogen (kg/ha)</Label>
                      <Input type="number" min="0" max="500" value={overrides.N} onChange={(e) => setOverrides({...overrides, N: Number(e.target.value)})} className="mt-1" />
                    </div>
                    <div>
                      <Label className="text-sm">Phosphorus (kg/ha)</Label>
                      <Input type="number" min="0" max="200" value={overrides.P} onChange={(e) => setOverrides({...overrides, P: Number(e.target.value)})} className="mt-1" />
                    </div>
                    <div>
                      <Label className="text-sm">Potassium (kg/ha)</Label>
                      <Input type="number" min="0" max="400" value={overrides.K} onChange={(e) => setOverrides({...overrides, K: Number(e.target.value)})} className="mt-1" />
                    </div>
                  </div>
                )}

                {/* Run Button */}
                <Button
                  onClick={runSimulation}
                  disabled={loading || !pin}
                  className="w-full lg:w-auto py-3 text-lg gap-2"
                  size="lg"
                >
                  <Cpu className="w-5 h-5" />
                  Run Digital Twin Simulation
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Panel - Results */}
          <div className="space-y-6">
            {data?.ranked_crops?.length > 0 && activeCrop ? (
              <>
                {/* Top Crop Card */}
                <Card className="border-emerald-300 bg-gradient-to-br from-emerald-50 to-white relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-100 rounded-full blur-3xl opacity-50" />
                  <CardHeader className="relative">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="default" className="text-xs">Top Match</Badge>
                          <Badge variant="secondary" className="text-xs">{data?.setup_type === 'seasonal' || data?.setup_type === 'short-term' ? 'Seasonal' : 'Perennial'}</Badge>
                        </div>
                        <h2 className="text-2xl font-bold text-slate-900">{activeCrop?.name}</h2>
                                                <p className="text-sm text-slate-500">{activeCrop?.variety} • {activeCrop?.season} • {activeCrop?.days} days</p>
                      </div>
                      <div className="text-right">
                        <p className="text-4xl font-bold text-emerald-600">{activeCrop?.score_pct}%</p>
                        <p className="text-xs text-slate-500">Suitability Score</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="relative space-y-4">
                    {/* Key Metrics Row */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <MetricCard label="Yield / Acre" value={`${activeCrop?.digital_twin?.yield_per_acre_tonnes || 0} t`} icon={<Tractor className="w-4 h-4" />} />
                                                                  <MetricCard label="Total Yield" value={`${activeCrop?.digital_twin?.total_yield_tonnes || 0} t`} icon={<Package className="w-4 h-4" />} />
                                                                  <MetricCard label="Est. Revenue" value={`₹${activeCrop?.digital_twin?.estimated_revenue_inr?.toLocaleString('en-IN') || 0}`} icon={<IndianRupee className="w-4 h-4" />} />
                                                                  <MetricCard label="Water / Day" value={`${activeCrop?.digital_twin?.daily_water_liters?.toLocaleString('en-IN') || 0} L`} icon={<Droplets className="w-4 h-4" />} />
                    </div>

                    {/* SHAP Explainability */}
                    <div className="border-t pt-4">
                      <h4 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                        <Brain className="w-4 h-4 text-emerald-600" />
                        SHAP Feature Impact Breakdown
                      </h4>
                      <div className="space-y-2">
                        {activeCrop?.shap_breakdown?.map((s: { feature: string; impact: number }, i: number) => (
                          <div key={i} className="flex items-center gap-3">
                            <div className="w-36 text-xs text-slate-600 font-medium">{s.feature}</div>
                            <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  s.impact >= 0 ? 'bg-emerald-500' : 'bg-rose-500'
                                }`}
                                style={{ width: `${Math.abs(s.impact) * 100}%` }}
                              />
                            </div>
                            <div className="w-24 text-xs text-slate-500 text-right">
                              {s.impact >= 0 ? '+' : ''}{s.impact.toFixed(2)}
                            </div>
                          </div>
                        ))}
                      </div>
                      <p className="text-xs text-slate-500 mt-2">Green = favorable alignment | Red = deviation from crop optimum</p>
                    </div>

                    {/* Risk Indicators */}
                    <div className="border-t pt-4">
                      <h4 className="text-sm font-semibold text-slate-700 mb-3">Risk Assessment</h4>
                      <div className="grid grid-cols-3 gap-3">
                        {Object.entries(activeCrop?.digital_twin?.risks || {}).map(([key, val]: [string, unknown]) => (
                                                  <div key={key} className="p-3 bg-slate-50 rounded-lg text-center">
                                                    <p className="text-xs text-slate-500 capitalize">{key.replace('_', ' ')}</p>
                                                    <p className="text-sm font-medium text-slate-900 mt-1">{String(val)}</p>
                                                  </div>
                                                ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Ranked Crops Table */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Table className="w-5 h-5" />
                      Ranked Crop Suitability (Top 6)
                    </CardTitle>
                    <CardDescription>All {setupType === 'seasonal' ? 25 : 20} crops scored • Click row for details</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50">
                            <TableHead className="w-8">#</TableHead>
                            <TableHead>Crop</TableHead>
                            <TableHead className="hidden md:table-cell">Variety</TableHead>
                            <TableHead className="text-right">Score</TableHead>
                            <TableHead className="text-right hidden sm:table-cell">Yield/Acre</TableHead>
                            <TableHead className="text-right hidden md:table-cell">Revenue</TableHead>
                            <TableHead className="text-right">Water/Day</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {(data?.ranked_crops || []).map((crop: any, idx: number) => (
                            <TableRow
                                key={`${crop.name}-${idx}`}
                              className={`cursor-pointer transition-colors ${selectedCropIndex === idx ? 'bg-emerald-50' : 'hover:bg-slate-50'}`}
                              onClick={() => setSelectedCropIndex(idx)}
                            >
                              <TableCell className="font-mono text-sm text-slate-500">{idx + 1}</TableCell>
                              <TableCell className="font-medium">{crop.name}</TableCell>
                              <TableCell className="hidden md:table-cell text-sm text-slate-600">{crop.variety}</TableCell>
                              <TableCell className="text-right font-semibold">
                                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
                                  crop.score_pct >= 85 ? 'bg-emerald-100 text-emerald-700' :
                                  crop.score_pct >= 75 ? 'bg-blue-100 text-blue-700' :
                                  crop.score_pct >= 65 ? 'bg-amber-100 text-amber-700' :
                                  'bg-rose-100 text-rose-700'
                                }`}>
                                  {crop.score_pct}%
                                </span>
                              </TableCell>
                              <TableCell className="text-right hidden sm:table-cell text-sm text-slate-700">
                                {crop.digital_twin?.yield_per_acre_tonnes ?? 0} t
                              </TableCell>
                              <TableCell className="text-right hidden md:table-cell text-sm text-slate-700 font-medium">
                                ₹{(crop.digital_twin?.estimated_revenue_inr ?? 0).toLocaleString('en-IN')}
                              </TableCell>
                              <TableCell className="text-right text-sm text-slate-700">
                                {(crop.digital_twin?.daily_water_liters ?? 0).toLocaleString('en-IN')} L
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>

                {/* Timeline / Agronomy Calendar */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      Agronomy Timeline — {activeCrop?.name || 'Crop'}
                    </CardTitle>
                    <CardDescription>Stage-wise schedule with weather-aligned advisories</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {(activeCrop?.timeline || []).map((stage: any, idx: number) => (
                        <div key={idx} className="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-100">
                          <div className="flex-shrink-0 w-16 h-16 rounded-xl bg-white border border-slate-200 flex items-center justify-center">
                            <span className="text-2xl font-bold text-emerald-600">{idx + 1}</span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <h5 className="font-semibold text-slate-900">{stage.stage_name}</h5>
                            <p className="text-xs text-slate-500 mt-0.5">{stage.days} days</p>
                            <p className="text-sm text-slate-700 mt-2 whitespace-pre-wrap">{stage.agronomy_advice}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="mt-4 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                      <p className="text-sm text-emerald-800">
                        <strong>Total Cycle:</strong> {(activeCrop?.timeline || []).reduce((a: number, b: any) => a + (Number(b.days) || 0), 0)} days (~{Math.round((activeCrop?.timeline || []).reduce((a: number, b: any) => a + (Number(b.days) || 0), 0) / 30)} months)
                        {' | '}
                        <strong>Total Water:</strong> {(activeCrop?.digital_twin?.total_water_m3 || 0).toLocaleString('en-IN')} m³
                        {' | '}
                        <strong>Projected Gross:</strong> ₹{(activeCrop?.digital_twin?.estimated_revenue_inr || 0).toLocaleString('en-IN')}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Rainfall Forecast */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <CloudRain className="w-5 h-5" />
                      6-Month Rainfall Forecast (Heuristic)
                    </CardTitle>
                    <CardDescription>Seasonal distribution based on agro-zone climatology</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                      {(data?.rainfall_forecast || []).map((m: any, idx: number) => (
                        <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-center">
                          <p className="text-xs text-slate-500">{m.month}</p>
                          <p className="text-2xl font-bold text-emerald-600 mt-1">{m.predicted_mm} mm</p>
                          <p className={`text-xs mt-1 ${m.anomaly_pct >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                            {m.anomaly_pct >= 0 ? '+' : ''}{m.anomaly_pct}% vs normal
                          </p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

              </> ) : (
              <>
                {/* Empty State */}
                <Card className="h-full min-h-[500px] flex flex-col items-center justify-center">
                  <div className="text-center">
                    <Cpu className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-slate-700 mb-2">Ready to Simulate</h3>
                    <p className="text-slate-500 mb-6 max-w-sm">
                      Pin your farm location on the map, configure parameters, and run the digital twin engine
                      to get AI-scored crop recommendations with SHAP explainability.
                    </p>
                    <div className="grid grid-cols-3 gap-4 text-sm text-center">
                      <div className="p-3 bg-slate-50 rounded-lg">
                        <p className="text-2xl font-bold text-emerald-600">45</p>
                        <p className="text-slate-500">Crops in Database</p>
                      </div>
                      <div className="p-3 bg-slate-50 rounded-lg">
                        <p className="text-2xl font-bold text-emerald-600">8</p>
                        <p className="text-slate-500">Indian Soil Profiles</p>
                      </div>
                      <div className="p-3 bg-slate-50 rounded-lg">
                        <p className="text-2xl font-bold text-emerald-600">5</p>
                        <p className="text-slate-500">Agro-Climatic Zones</p>
                      </div>
                    </div>
                  </div>
                </Card>
              </>
            )}

          </div>
        </div>
      </div>
    </main>
  );
}