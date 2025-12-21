import React,{useEffect,useState} from 'react';
import {
    BarChart3, Clock, CheckCircle, Plus,
    TrendingUp, MessageSquare, ArrowUpRight
} from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import axios from "axios";
import {useParams,useNavigate} from "react-router-dom";


// Mock Data Object
const MOCK_DATA = {
    overall_score: 82,
    interviews_done: 14,
    practice_time: "12.5 hrs",
    performance_history: [
        { day: 'Mon', score: 65 },
        { day: 'Tue', score: 72 },
        { day: 'Wed', score: 70 },
        { day: 'Thu', score: 78 },
        { day: 'Fri', score: 82 },
    ],
    recent_sessions: [
        { id: 1, role: "Frontend Engineer", score: 85, date: "Dec 18", status: "Completed" },
        { id: 2, role: "Python Backend", score: 78, date: "Dec 15", status: "Completed" },
        { id: 3, role: "System Design", score: 68, date: "Dec 12", status: "Completed" },
    ],
    ai_insight: "Your eye contact improved by 12% in your last session! Focus on slowing down your speech during technical explanations."
};



const Dashboard = () => {

    const [username,setUsername] = useState("");
    const {userId}= useParams();
    const navigate = useNavigate();



        useEffect(() => {
            const fetchStats = async () => {
                try {
                    const response = await axios.get(
                        `http://localhost:8080/api/users/${userId}`
                    );
                    setUsername(response.data.username);
                } catch (err) {
                    console.error(err);
                    alert("Error fetching user info");
                }
            };

           void fetchStats()
        }, [username,userId,setUsername]);



    return (

        <div className="min-h-screen bg-slate-950 text-slate-200 p-4 md:p-8 font-sans">
            {/* Header Section */}
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
                <div>
                    <h1 className="text-4xl font-extrabold text-white tracking-tight">
                        Welcome, <span className="text-sky-400">{`${username}`}</span>
                    </h1>
                    <p className="text-slate-400 mt-1">Your interview readiness is looking sharp today.</p>
                </div>
                <button className="group flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-sky-500 hover:from-indigo-500 hover:to-sky-400 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-indigo-500/20 active:scale-95"
                 onClick={() => {
                     navigate(`/interview/${userId}`);
                 }}>
                    <Plus size={20} />
                    Start New Interview
                </button>
            </header>

            {/* Stats Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <StatCard icon={<TrendingUp className="text-sky-400" />} label="Average AceScore" value={`${MOCK_DATA.overall_score}%`} trend="+4% from last week" />
                <StatCard icon={<CheckCircle className="text-indigo-400" />} label="Interviews Completed" value={MOCK_DATA.interviews_done} trend="Top 15% of users" />
                <StatCard icon={<Clock className="text-sky-400" />} label="Total Practice Time" value={MOCK_DATA.practice_time} trend="3 sessions this week" />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Chart Placeholder (Left 2 columns) */}
                <div className="lg:col-span-2 bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <BarChart3 size={20} className="text-indigo-400" /> Performance Trend
                        </h3>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={MOCK_DATA.performance_history}>
                                <defs>
                                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                                        <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                                <XAxis dataKey="day" stroke="#64748b" axisLine={false} tickLine={false} />
                                <YAxis hide />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                                    itemStyle={{ color: '#38bdf8' }}
                                />
                                <Area type="monotone" dataKey="score" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Sidebar: Feed & Insights */}
                <div className="flex flex-col gap-6">
                    {/* AI Insight Card */}
                    <div className="bg-gradient-to-br from-indigo-900/40 to-slate-900 border border-indigo-500/30 p-5 rounded-2xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <MessageSquare size={80} />
                        </div>
                        <h3 className="text-sm font-bold text-indigo-300 uppercase tracking-widest mb-3">Top AI Insight</h3>
                        <p className="text-slate-200 leading-relaxed italic">"{MOCK_DATA.ai_insight}"</p>
                    </div>

                    {/* Activity Feed */}
                    <div className="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <h3 className="text-lg font-bold mb-4">Recent Sessions</h3>
                        <div className="space-y-4">
                            {MOCK_DATA.recent_sessions.map((session) => (
                                <div key={session.id} className="flex items-center justify-between p-3 bg-slate-800/40 rounded-xl hover:bg-slate-800 transition-colors cursor-pointer group">
                                    <div>
                                        <p className="font-semibold text-sm group-hover:text-sky-400 transition-colors">{session.role}</p>
                                        <p className="text-xs text-slate-500">{session.date}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-bold text-white">{session.score}/100</p>
                                        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20">
                      {session.status}
                    </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

const StatCard = ({ icon, label, value, trend }) => (
    <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl hover:border-slate-700 transition-all shadow-xl">
        <div className="bg-slate-800 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
            {icon}
        </div>
        <p className="text-slate-400 text-sm font-medium">{label}</p>
        <h2 className="text-3xl font-bold text-white my-1">{value}</h2>
        <p className="text-xs text-slate-500 flex items-center gap-1">
            <ArrowUpRight size={14} className="text-emerald-400" /> {trend}
        </p>
    </div>
);

export default Dashboard;