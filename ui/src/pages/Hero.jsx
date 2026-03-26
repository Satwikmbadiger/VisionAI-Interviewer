import logo from '../assets/logo.png'
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import React from 'react';
import { useNavigate } from 'react-router-dom';
import Robot from '../Component/Robot.jsx'
import '../Styles/App.css'

export default function Hero() {
    const navigate = useNavigate()

    return (
        /* FIXED: Changed min-h-screen to h-screen and added overflow-hidden */
        <div className="h-screen w-full flex flex-col bg-[#0f172a] bg-gradient-to-b from-[#0f172a] to-[#334155] text-slate-200 font-sans overflow-hidden">

            {/* NAVBAR: Keep h-20 */}
            <nav className="h-20 flex flex-shrink-0 justify-between items-center px-8 bg-slate-950/40 backdrop-blur-xl border-b border-white/5 z-50">
                <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 rounded-xl overflow-hidden ring-2 ring-sky-500/20">
                        <img src={logo} alt="logo" className="h-full w-full object-cover" />
                    </div>
                    <p className="font-bold text-2xl text-slate-50 tracking-tight">
                        Vision<span className="text-sky-400">AI</span>
                    </p>
                </div>

                <ul className="flex flex-row items-center space-x-8 text-slate-300 font-medium">
                    <li><a href="#" className="hover:text-sky-400 transition-colors">About Us</a></li>
                    <li>
                        <button
                            className="bg-white/10 hover:bg-white/20 text-slate-50 px-6 py-2 rounded-lg font-semibold border border-white/10 transition-all active:scale-95 "
                            onClick={() => navigate('/users/login')}
                        >
                            Login
                        </button>
                    </li>
                </ul>
            </nav>

            {/* MAIN: flex-1 takes the remaining height (100vh - 80px) */}
            <main className="flex flex-row flex-1 overflow-hidden px-12">

                {/* Left Side: Using justify-evenly to distribute space vertically */}
                <div className="flex-[1.5] flex flex-col justify-evenly py-8 pr-6">

                    <div className="space-y-6">
                        {/* Demo Badge */}
                        <div className="inline-flex items-center gap-2 bg-sky-500/10 px-4 py-1.5 rounded-full border border-sky-500/20">
                            <div className="w-2 h-2 bg-sky-400 rounded-full animate-pulse"></div>
                            <span className="font-semibold text-sky-400 text-xs uppercase tracking-wider">Live Demo</span>
                        </div>

                        {/* Heading */}
                        <h1 className="font-extrabold text-5xl xl:text-7xl leading-[1.1] tracking-tight text-slate-50">
                            Master your presence,
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400 block">
                                perfect every cue.
                            </span>
                        </h1>

                        {/* Quote */}
                        <h2 className="text-lg md:text-xl font-normal text-slate-300 leading-relaxed italic border-l-4 border-sky-500/30 pl-6 max-w-xl">
                            Master the art of the interview. Turn every gesture and word into a winning first impression.                        </h2>
                    </div>

                    {/* CTA Button */}
                    <div>
                        <button
                            className="group bg-indigo-600 text-white h-[60px] px-10 rounded-2xl text-xl font-bold flex items-center gap-4 hover:bg-indigo-500 hover:shadow-[0_0_30px_rgba(99,102,241,0.4)] transition-all duration-300 active:scale-95"
                            id={"shine-button"}
                            onClick={() => navigate('/users/new')}
                        >
                            <span>Get Started</span>
                            <ArrowForwardIosIcon sx={{ fontSize: 20 }} className="group-hover:translate-x-1 transition-transform" />
                        </button>
                    </div>

                    {/* Stats */}
                    <div className="flex flex-row gap-12 pt-6 border-t border-white/5">
                        <div>
                            <p className="font-bold text-3xl text-slate-50">2.5K+</p>
                            <p className="text-slate-400 text-sm font-medium">Members</p>
                        </div>
                        <div>
                            <p className="font-bold text-3xl text-slate-50">15K+</p>
                            <p className="text-slate-400 text-sm font-medium">Traded</p>
                        </div>
                        <div>
                            <p className="font-bold text-3xl text-slate-50">98%</p>
                            <p className="text-slate-400 text-sm font-medium">Happy</p>
                        </div>
                    </div>
                </div>

                {/* Right Side */}
                <div className="flex-1 flex justify-center items-center relative">
                    <div className="absolute w-[350px] h-[350px] bg-sky-500/10 blur-[100px] rounded-full"></div>
                    <div className="relative z-10 scale-90 xl:scale-100">
                        <Robot/>
                    </div>
                </div>
            </main>
        </div>
    )
}