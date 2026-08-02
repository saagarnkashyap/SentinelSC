import streamlit as st

def load_theme():
    st.markdown("""
    <style>

    .block-container{
        padding-top:2rem;
        padding-bottom:2rem;
    }
    .hero h1{

font-size:60px;

margin-bottom:6px;

font-weight:800;

}

.hero p{

font-size:20px;

color:#9ca3af;

margin-bottom:28px;

}

    /* ===============================
   LIVE STATUS
================================ */

.status-wrapper{
    display:flex;
    align-items:center;
    gap:14px;
    margin-top:20px;
    margin-bottom:30px;
}

.live-dot{
    width:10px;
    height:10px;
    border-radius:50%;
    background:#34d399;

    box-shadow:
        0 0 5px #34d399,
        0 0 12px rgba(0,255,136,.45);

    animation:pulse 1.6s ease-in-out infinite;
}

.status-text{
    display:flex;
    align-items:center;
}

.live-text{
    color:#34d399;
    font-size:18px;
    font-weight:700;
    letter-spacing:1px;
}

.system-text{
    color:#b7bcc7;
    font-size:18px;
    margin-left:8px;
}

@keyframes pulse{

    0%{
        transform:scale(1);
        opacity:1;
    }

    50%{
        transform:scale(1.35);
        opacity:.45;
    }

    100%{
        transform:scale(1);
        opacity:1;
    }

}

    @keyframes pulse{

        0%{
            transform:scale(0.9);
            opacity:1;
        }

        50%{
            transform:scale(1.35);
            opacity:.45;
        }

        100%{
            transform:scale(0.9);
            opacity:1;
        }

    }

    </style>
    """, unsafe_allow_html=True)