

const BACKEND_URL = ""; // JS-only GBM engine — no backend required

function switchSection(id, navEl) {
  document.querySelectorAll('.dash-section').forEach(function(s) { s.style.display = 'none'; });
  var target = document.getElementById('section-' + id);
  if (target) target.style.display = '';

  document.querySelectorAll('.nav-item').forEach(function(n) {
    n.classList.remove('active');
    var dot = n.querySelector('.nav-dot');
    if (dot) dot.remove();
  });
  if (navEl) {
    navEl.classList.add('active');
    var dot = document.createElement('div');
    dot.className = 'nav-dot';
    navEl.appendChild(dot);
  }

  var rp = document.querySelector('.right-panel');
  if (rp) rp.style.display = (id === 'simulation' && document.getElementById('pdSimSection') && document.getElementById('pdSimSection').classList.contains('open')) ? '' : 'none';

  if (typeof DASHBOARD_DATA !== 'undefined') renderSectionData(id);
}

function handleLogout() {
  try {
    var pd = window.parent.document;
    var url = new URL(window.parent.location.href);
    url.searchParams.set('nav', 'landing');
    window.parent.location.href = url.toString();
  } catch (e) {
    try {
      window.top.location.href = '/?nav=landing';
    } catch (e2) {
      window.location.href = '/?nav=landing';
    }
  }
}

let _sectionChartsRendered = {};
function renderSectionData(id) {
  var D = (typeof DASHBOARD_DATA !== 'undefined') ? DASHBOARD_DATA : {};

    if (id === 'overview') {
    setText('ovDate', new Date().toLocaleDateString('en-US',{weekday:'long',year:'numeric',month:'long',day:'numeric'}));

    if (D.portfolio_value) {
      var pv = D.portfolio_value;
      var label = pv >= 1e9 ? (pv/1e9).toFixed(2)+'B' : pv >= 1e6 ? (pv/1e6).toFixed(1)+'M' : pv >= 1e3 ? (pv/1e3).toFixed(0)+'K' : pv.toFixed(0);
      setText('ovPortfolio', '$' + label);
    } else {
      setText('ovPortfolio', '$' + (D.total_assets ? (D.total_assets/1e9).toFixed(2)+'B' : '0.00'));
    }
    setText('ovRiskScore', D.ai_risk_score || '0');
    var riskBadge = document.getElementById('ovRiskBadge');
    if (riskBadge && D.ai_risk_label) {
      riskBadge.textContent = D.ai_risk_label;
      riskBadge.className = 'ov-kpi-badge badge-' + D.ai_risk_label.toLowerCase();
    }
    setText('ovESG', D.avg_esg || '0.0');
    setText('ovHighRiskPct', (D.high_risk_pct || 0) + '%');

    if (D.risk_intelligence) {
      var dotColors = ['#3B82F6','#F59E0B','#EF4444','#10B981'];
      var html = '';
      D.risk_intelligence.forEach(function(msg, i) {
        html += '<div class="ov-intel-item"><div class="ov-intel-dot" style="background:'+dotColors[i%dotColors.length]+'"></div><div class="ov-intel-text">'+msg+'</div></div>';
      });
      var el = document.getElementById('ovIntelList');
      if (el) el.innerHTML = html;
    }

    setText('ovRegName2', D.reg_name || '--');
    setText('ovR2Val', D.r2 || '--');
    setText('ovClsName2', D.cls_name || '--');
    setText('ovAUCVal', D.auc || '--');
    setText('ovCluName2', D.clu_name || '--');
    setText('ovCluCount', D.n_clusters || '--');

    if (D.confusion_matrix) {
      var cm = D.confusion_matrix;
      var el = document.getElementById('ovConfMatrix');
      if (el) {
        el.innerHTML =
          '<div class="cm-header"></div><div class="cm-header">Pred 0</div><div class="cm-header">Pred 1</div>' +
          '<div class="cm-header">Act 0</div><div class="cm-cell cm-tn" title="True Negatives: Correctly identified Low Risk">'+cm[0][0]+'</div><div class="cm-cell cm-fp" title="False Positives: Low risk incorrectly flagged as High">'+cm[0][1]+'</div>' +
          '<div class="cm-header">Act 1</div><div class="cm-cell cm-fn" title="False Negatives: High risk missed">'+cm[1][0]+'</div><div class="cm-cell cm-tp" title="True Positives: Correctly identified High Risk">'+cm[1][1]+'</div>';
      }
      
      var metricsHTML = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px;padding-top:14px;border-top:1px solid #eee">' +
        '<div style="text-align:center"><div style="font-size:10px;color:var(--text-3);text-transform:uppercase">Accuracy</div><div style="font-weight:700;color:var(--text)">'+(D.accuracy||'--')+'</div></div>' +
        '<div style="text-align:center"><div style="font-size:10px;color:var(--text-3);text-transform:uppercase">Precision</div><div style="font-weight:700;color:var(--text)">'+(D.precision||'--')+'</div></div>' +
        '<div style="text-align:center"><div style="font-size:10px;color:var(--text-3);text-transform:uppercase">Recall</div><div style="font-weight:700;color:var(--text)">'+(D.recall||'--')+'</div></div>' +
        '</div>';
      var cont = document.getElementById('ovCMContainer');
      if (cont) {
        var existingMetrics = document.getElementById('ovMetricsRow');
        if (existingMetrics) {
          existingMetrics.innerHTML = metricsHTML;
        } else {
          var div = document.createElement('div');
          div.id = 'ovMetricsRow';
          div.innerHTML = metricsHTML;
          cont.appendChild(div);
        }
      }
    }

    var selF = document.getElementById('ovFilterSector');
    if (D.sector_risk && selF && !selF._populated) {
      D.sector_risk.labels.forEach(function(l) {
        var opt = document.createElement('option');
        opt.value = l; opt.textContent = l;
        selF.appendChild(opt);
      });
      selF._populated = true;
    }

    if (D.risky_entities) {
      window._ovRiskyData = D.risky_entities;
      window._ovSortCol = -1;
      window._ovSortAsc = true;
      renderRiskyTable(D.risky_entities);
    }

    if (D.feat_labels) {
      var explainHTML = '<div style="margin-bottom:16px">';
      D.feat_labels.forEach(function(f, i) {
        var pctV = (D.feat_values[i]*100).toFixed(1);
        var barC = i === 0 ? '#EF4444' : i === 1 ? '#F59E0B' : '#3B82F6';
        explainHTML += '<div style="margin-bottom:10px"><div style="display:flex;justify-content:space-between;margin-bottom:3px"><span style="font-weight:600;color:var(--text)">'+f+'</span><span>'+pctV+'%</span></div>';
        explainHTML += '<div style="height:6px;background:#F3F4F6;border-radius:3px;overflow:hidden"><div style="height:100%;width:'+pctV+'%;background:'+barC+';border-radius:3px"></div></div></div>';
      });
      explainHTML += '</div><p style="font-size:12px;color:var(--text-3)">Features ranked by model importance. <strong>'+D.feat_labels[0]+'</strong> is the strongest predictor of high risk.</p>';
      var el = document.getElementById('ovShapExplain');
      if (el) el.innerHTML = explainHTML;
    }

    if (D.cluster_labels) {
      var clColors = {'High ESG, Low Risk':'#ECFDF5;color:#059669','High ESG, High Risk':'#FEF2F2;color:#DC2626','Low ESG, Low Risk':'#EFF6FF;color:#3B82F6','Low ESG, High Risk':'#FFFBEB;color:#D97706'};
      var clHTML = '';
      Object.keys(D.cluster_labels).forEach(function(k) {
        var lbl = D.cluster_labels[k];
        var style = clColors[lbl] || '#F3F4F6;color:var(--text)';
        clHTML += '<span class="cluster-segment" style="background:'+style+'">Cluster '+k+': '+lbl+'</span>';
      });
      var el = document.getElementById('ovCluLabels');
      if (el) el.innerHTML = clHTML;
    }

    if (!_sectionChartsRendered.overview) {
      _sectionChartsRendered.overview = true;

      if (D.reg_feat_labels) {
        var ctx = document.getElementById('ovRegFeatChart');
        if (ctx) new Chart(ctx, { type:'bar', data:{labels:D.reg_feat_labels,datasets:[{data:D.reg_feat_values,backgroundColor:'rgba(124,58,237,0.7)',borderRadius:4,borderSkipped:false}]}, options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(0,0,0,0.04)'}},y:{grid:{display:false}}}} });
      }

      if (D.feat_labels) {
        var ctx = document.getElementById('ovShapChart');
        if (ctx) new Chart(ctx, { type:'bar', data:{labels:D.feat_labels,datasets:[{data:D.feat_values,backgroundColor:['#EF4444','#F59E0B','#3B82F6','#10B981','#7c6cf0','#EC4899','#06B6D4','#8B5CF6'].slice(0,D.feat_labels.length),borderRadius:4,borderSkipped:false}]}, options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(0,0,0,0.04)'}},y:{grid:{display:false}}}} });
      }

      if (D.cluster_rows) {
        var labels = D.cluster_rows.map(function(r){return 'Cluster '+r[0];});
        var vals = D.cluster_rows.map(function(r){return r.length > 1 ? r[1] : 1;});
        var ctx = document.getElementById('ovCluDistChart');
        if (ctx) new Chart(ctx, { type:'doughnut', data:{labels:labels,datasets:[{data:vals,backgroundColor:['#3B82F6','#10B981','#F59E0B','#EF4444','#7c6cf0','#EC4899'],borderWidth:0}]}, options:{responsive:true,maintainAspectRatio:false,cutout:'70%',plugins:{legend:{position:'bottom',labels:{boxWidth:8,font:{size:10}}}}} });
      }

      if (D.sector_risk) {
        var ctx = document.getElementById('ovSectorRiskChart');
        if (ctx) new Chart(ctx, { type:'bar', data:{labels:D.sector_risk.labels,datasets:[{label:'Avg Risk',data:D.sector_risk.values,backgroundColor:D.sector_risk.values.map(function(v){return v>16?'rgba(239,68,68,0.7)':v>14?'rgba(245,158,11,0.7)':'rgba(16,185,129,0.7)';}),borderRadius:6,borderSkipped:false}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'rgba(0,0,0,0.04)'},beginAtZero:true}}} });
        if (D.sector_risk_insight) { var el = document.getElementById('ovSectorInsight'); if(el) el.innerHTML = '<strong>Insight:</strong> ' + D.sector_risk_insight; }
      }

      if (D.env !== undefined) {
        var envP=((D.env||0)*100).toFixed(1), socP=((D.soc||0)*100).toFixed(1), govP=((D.gov||0)*100).toFixed(1);
        setText('ovEnvScore',envP); setText('ovSocScore',socP); setText('ovGovScore',govP);
        var ctx = document.getElementById('ovEsgRadar');
        if (ctx) new Chart(ctx, { type:'radar', data:{labels:['Environment','Social','Governance'],datasets:[{label:'ESG',data:[parseFloat(envP),parseFloat(socP),parseFloat(govP)],backgroundColor:'rgba(16,185,129,0.15)',borderColor:'#10B981',borderWidth:2.5,pointBackgroundColor:'#fff',pointBorderColor:'#10B981',pointRadius:5}]}, options:{responsive:true,maintainAspectRatio:false,scales:{r:{beginAtZero:true,max:100,ticks:{stepSize:20,font:{size:10}},grid:{color:'rgba(0,0,0,0.06)'}}},plugins:{legend:{display:false}}} });
      }

      if (D.risk_timeseries) {
        var ctx = document.getElementById('ovRiskTrendChart');
        if (ctx) new Chart(ctx, { type:'line', data:{labels:D.risk_timeseries.labels,datasets:[{label:'Risk Score',data:D.risk_timeseries.values,borderColor:'#EF4444',backgroundColor:'rgba(239,68,68,0.08)',borderWidth:2.5,pointRadius:4,pointBackgroundColor:'#fff',pointBorderColor:'#EF4444',fill:true,tension:0.4}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'rgba(0,0,0,0.04)'},beginAtZero:false}}} });
      }

      if (D.esg_trend) {
        var ctx = document.getElementById('ovEsgTrendChart2');
        if (ctx) new Chart(ctx, { type:'line', data:{labels:D.esg_trend.labels,datasets:[{label:'ESG Score',data:D.esg_trend.data,borderColor:'#10B981',backgroundColor:'rgba(16,185,129,0.08)',borderWidth:2.5,pointRadius:4,pointBackgroundColor:'#fff',pointBorderColor:'#10B981',fill:true,tension:0.4}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'rgba(0,0,0,0.04)'},beginAtZero:false}}} });
      }
    }
  }

  if (id === 'credit') {
    setText('crAUC', D.auc || '—');
    setText('crHighRisk', D.high_risk || '0');
    setText('crTotal', (D.credit_total || 0).toLocaleString());
    setText('crModel', D.cls_name || '—');
    if (D.feat_labels && !_sectionChartsRendered.feature) {
      _sectionChartsRendered.feature = true;
      var ctx = document.getElementById('featureChart');
      if (ctx) new Chart(ctx, {
        type: 'bar',
        data: { labels: D.feat_labels, datasets: [{ label: 'Impact',
          data: D.feat_values, backgroundColor: 'rgba(16,185,129,0.7)',
          borderRadius: 6, borderSkipped: false }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { x: { grid: { color: 'rgba(0,0,0,0.04)' } }, y: { grid: { display: false } } } }
      });
    }
    if (D.high_risk) {
      var pctVal = ((D.high_risk / D.credit_total) * 100).toFixed(1);
      var el = document.getElementById('crBreakdown');
      if (el) el.innerHTML =
        '<div class="insight-item" style="margin-bottom:10px"><div class="insight-icon" style="background:#FEF2F2">⚠️</div><div><div class="insight-text"><strong>' + D.high_risk + '</strong> entities (' + pctVal + '%) exceed the 90th-pctl risk threshold.</div></div></div>' +
        '<div class="insight-item" style="margin-bottom:10px"><div class="insight-icon" style="background:#ECFDF5">✅</div><div><div class="insight-text"><strong>' + (D.credit_total - D.high_risk) + '</strong> entities within acceptable risk bounds.</div></div></div>';
    }
  }

  if (id === 'esg') {
    setText('esgScore', D.avg_esg || '0.0');
    var envP = ((D.env || 0) * 100).toFixed(1), socP = ((D.soc || 0) * 100).toFixed(1), govP = ((D.gov || 0) * 100).toFixed(1);
    setText('esgEnv', envP + '%'); setText('esgSoc', socP + '%'); setText('esgGov', govP + '%');
    
    if (D.esg_count) {
       setText('esgDataContext', 'Updated Today | Based on ' + D.esg_count.toLocaleString() + ' tracked entities');
    }

    if (D.esg_sub) {
       setText('envCarbon', D.esg_sub.env.carbon);
       setText('envEnergy', D.esg_sub.env.energy);
       setText('envWater', D.esg_sub.env.water);
       setText('socTurnover', D.esg_sub.soc.turnover);
       setText('socDiversity', D.esg_sub.soc.diversity);
       setText('socSafety', D.esg_sub.soc.safety);
       setText('govBoard', D.esg_sub.gov.board_ind);
       setText('govCompliance', D.esg_sub.gov.compliance);
       setText('govAudit', D.esg_sub.gov.audit);
    }

    if (D.esg_insights) {
       var insHTML = '';
       D.esg_insights.forEach(function(msg, i) {
           var colors = ['#10B981', '#7c6cf0', '#F59E0B'];
           insHTML += '<div style="display:flex;gap:12px;align-items:flex-start;">' +
                      '<div style="min-width:14px;height:14px;border-radius:50%;background:'+colors[i]+';margin-top:2px;"></div>' +
                      '<div style="font-size:13px;line-height:1.5;color:var(--text-1)">' + msg + '</div></div>';
       });
       var listEl = document.getElementById('esgInsightsList');
       if (listEl) listEl.innerHTML = insHTML;
    }

    if (!_sectionChartsRendered.esg) {
      _sectionChartsRendered.esg = true;
      
      if (D.esg_trend) {
         var ctxT = document.getElementById('esgTrendChart');
         if (ctxT) new Chart(ctxT, {
             type: 'line',
             data: { labels: D.esg_trend.labels, datasets: [{
                 label: 'ESG Score', data: D.esg_trend.data,
                 borderColor: '#10B981', backgroundColor: 'rgba(16,185,129,0.1)',
                 borderWidth: 2.5, pointRadius: 4, pointBackgroundColor: '#fff', pointBorderColor: '#10B981', fill: true, tension: 0.4
             }]},
             options: { responsive: true, maintainAspectRatio: false, 
                 plugins:{legend:{display:false}},
                 scales: {x:{grid:{display:false}}, y:{grid:{color:'rgba(0,0,0,0.04)', drawBorder:false}, beginAtZero: false}}
             }
         });
      }

      var ctxP = document.getElementById('esgPieChart');
      if (ctxP) new Chart(ctxP, {
          type: 'doughnut',
          data: { labels: ['Environment', 'Social', 'Governance'], datasets: [{
              data: [D.env||0, D.soc||0, D.gov||0],
              backgroundColor: ['#10B981', '#7c6cf0', '#F59E0B'],
              borderWidth: 0, hoverOffset: 4
          }]},
          options: { responsive: true, maintainAspectRatio: false, cutout: '75%', plugins: {legend: {position:'right', labels:{usePointStyle:true, padding:15, font:{size:12, family:"'Plus Jakarta Sans', sans-serif"}}}} }
      });

      if (D.esg_points) {
          var d = D.esg_points;
          var trace = {
              x: d.x, y: d.y, z: d.z,
              mode: 'markers',
              marker: { size: 5, color: d.c, colorscale: 'Viridis', opacity: 0.8, line: { width: 0.5, color: '#ffffff' } },
              type: 'scatter3d'
          };
          var layout = {
              margin: { l: 0, r: 0, b: 0, t: 0 },
              scene: {
                  xaxis: { title: 'Environment', backgroundcolor: 'transparent', gridcolor: '#e5e7eb', showbackground: false },
                  yaxis: { title: 'Social', backgroundcolor: 'transparent', gridcolor: '#e5e7eb', showbackground: false },
                  zaxis: { title: 'Governance', backgroundcolor: 'transparent', gridcolor: '#e5e7eb', showbackground: false }
              },
              paper_bgcolor: 'transparent', plot_bgcolor: 'transparent'
          };
          var esgCanvas = document.getElementById('esgChart');
          if (esgCanvas) {
              var parent = esgCanvas.parentElement;
              parent.removeChild(esgCanvas);
              var plotlyDiv = document.createElement('div');
              plotlyDiv.id = 'esgPlotlyDiv';
              plotlyDiv.style.width = '100%';
              plotlyDiv.style.height = '100%';
              parent.appendChild(plotlyDiv);
              Plotly.newPlot('esgPlotlyDiv', [trace], layout, {responsive: true, displayModeBar: false});
          }
      }
    }
  }

  if (id === 'clustering') {
    setText('cluCount', D.n_clusters || '—');
    setText('cluModel', D.clu_name || '—');
    setText('cluEntities', (D.entity_count || 0).toLocaleString());
    if (D.cluster_cols && D.cluster_rows) {
      var t = '<table style="width:100%;border-collapse:collapse;font-size:13px">';
      t += '<tr>' + D.cluster_cols.map(function(c){return '<th style="text-align:left;padding:8px 10px;border-bottom:2px solid #E5E7EB;color:var(--text-2);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px">'+c+'</th>';}).join('') + '</tr>';
      D.cluster_rows.forEach(function(r,i){
        t += '<tr style="background:'+(i%2?'#F9FAFB':'#fff')+'">' + r.map(function(v){return '<td style="padding:8px 10px;border-bottom:1px solid #F3F4F6">'+v+'</td>';}).join('') + '</tr>';
      });
      t += '</table>';
      document.getElementById('cluTable').innerHTML = t;
    }
    if (!_sectionChartsRendered.cluster) {
      _sectionChartsRendered.cluster = true;

      var x1D = [];
      var y1D = [];
      var z2D = [];
      for(var i=-3; i<=3.1; i+=0.2){
          x1D.push(i);
          y1D.push(i);
      }
      for(var i=0; i<y1D.length; i++){
          var z_row = [];
          for(var j=0; j<x1D.length; j++){
              z_row.push(x1D[j]*x1D[j] + y1D[i]*y1D[i]);
          }
          z2D.push(z_row);
      }
      
      var surfaceTrace = {
          z: z2D,
          x: x1D,
          y: y1D,
          type: 'surface',
          colorscale: 'RdBu',
          reversescale: true,
          showscale: false,
          opacity: 0.8
      };

      var pathX = [];
      var pathY = [];
      var pathZ = [];
      var currX = 2.5;
      var currY = 1.0;
      var learningRate = 0.08;
      
      for(var step=0; step<20; step++){
          pathX.push(currX);
          pathY.push(currY);
          pathZ.push(currX*currX + currY*currY + 0.2); // slight offset so line is visible above surface
          var gradX = 2 * currX;
          var gradY = 2 * currY;
          currX = currX - learningRate * gradX;
          currY = currY - learningRate * gradY;
      }
      
      var pathTrace = {
          x: pathX,
          y: pathY,
          z: pathZ,
          mode: 'lines+markers',
          type: 'scatter3d',
          marker: {size: 4, color: '#000000'},
          line: {color: '#000000', width: 3},
          name: 'Descent Path'
      };

      var layout = {
        margin:{l:0,r:0,b:0,t:0},
        scene:{
          xaxis:{title:'Parameter 1',gridcolor:'#e5e7eb',showbackground:false},
          yaxis:{title:'Parameter 2',gridcolor:'#e5e7eb',showbackground:false},
          zaxis:{title:'Loss',gridcolor:'#e5e7eb',showbackground:false},
          aspectratio: {x: 1, y: 1, z: 0.7},
          camera: { eye: {x: 1.3, y: -1.3, z: 0.7} }
        },
        paper_bgcolor:'transparent',plot_bgcolor:'transparent',
        showlegend: false
      };
      
      Plotly.newPlot('cluPlotlyWrap',[surfaceTrace, pathTrace],layout,{responsive:true,displayModeBar:false});
    }
  }
}

function setText(id, val) {
  var el = document.getElementById(id);
  if (el) el.textContent = val;
}

let pathsChartInst = null;
let histChartInst  = null;
let currentTab     = "nominal";
let lastResultA    = null;
let lastResultB    = null;

(function initDateTime() {
  const now = new Date();
  var dateEl = document.getElementById("dateText");
  if (dateEl) dateEl.textContent =
    now.toLocaleDateString("en-US", { weekday:"long", year:"numeric", month:"long", day:"numeric" });
})();

const fmt = (n, dec=0) =>
  "$" + Number(n).toLocaleString("en-US", {minimumFractionDigits:dec, maximumFractionDigits:dec});
const pct = (n, dec=1) => Number(n).toFixed(dec) + "%";

function randn() {
  let u=0, v=0;
  while(u===0) u=Math.random();
  while(v===0) v=Math.random();
  return Math.sqrt(-2*Math.log(u)) * Math.cos(2*Math.PI*v);
}

function percentile(sorted, p) {
  const i = (p/100)*(sorted.length-1);
  const lo = Math.floor(i), hi = Math.ceil(i);
  return sorted[lo] + (sorted[hi]-sorted[lo])*(i-lo);
}

const mean = a => a.reduce((s,x)=>s+x,0)/a.length;

function std(a) {
  const m=mean(a);
  return Math.sqrt(a.reduce((s,x)=>s+(x-m)**2,0)/a.length);
}

function runGBM(params) {
  const { S0, years, mu, sigma, inflation, nSims, monthly } = params;
  const steps   = years * 12;
  const dt      = 1/12;
  const realMu  = (1+mu)/(1+inflation) - 1;
  const nomDrift  = (mu    - 0.5*sigma*sigma) * dt;
  const realDrift = (realMu - 0.5*sigma*sigma) * dt;
  const diff      = sigma * Math.sqrt(dt);

  const paths     = [];  // nominal
  const realPaths = [];
  const finalNom  = [];
  const finalReal = [];

  for (let i=0; i<nSims; i++) {
    const pNom  = [S0];
    const pReal = [S0];
    let sN=S0, sR=S0;
    for (let t=0; t<steps; t++) {
      const z = randn();
      sN = sN * Math.exp(nomDrift  + diff*z) + monthly;
      sR = sR * Math.exp(realDrift + diff*z) + monthly;
      pNom.push(sN);
      pReal.push(sR);
    }
    paths.push(pNom);
    realPaths.push(pReal);
    finalNom.push(sN);
    finalReal.push(sR);
  }
  return { paths, realPaths, finalNom, finalReal };
}

function buildBands(paths) {
  if (!paths.length) return {};
  const steps = paths[0].length;
  const mean_=[], p5_=[], p25_=[], p75_=[], p95_=[];
  for (let t=0; t<steps; t++) {
    const col = paths.map(p=>p[t]).sort((a,b)=>a-b);
    mean_.push(mean(col));
    p5_.push(percentile(col,5));
    p25_.push(percentile(col,25));
    p75_.push(percentile(col,75));
    p95_.push(percentile(col,95));
  }
  return { mean:mean_, p5:p5_, p25:p25_, p75:p75_, p95:p95_ };
}

function computeMetrics(finals, S0) {
  const sorted = [...finals].sort((a,b)=>a-b);
  const m = mean(finals);
  const s = std(finals);
  const p50 = percentile(sorted,50);
  const p5  = percentile(sorted,5);
  const p25 = percentile(sorted,25);
  const p75 = percentile(sorted,75);
  const p95 = percentile(sorted,95);
  const probLoss = finals.filter(v=>v<S0).length/finals.length*100;
  const VaR = S0 - p5;
  return { mean:m, median:p50, p5, p25, p75, p95, std:s, probLoss, VaR };
}

function makeHistogram(vals, bins=50) {
  const min=Math.min(...vals), max=Math.max(...vals);
  const width=(max-min)/bins;
  const counts=new Array(bins).fill(0);
  vals.forEach(v => {
    let b=Math.floor((v-min)/width);
    if(b===bins) b=bins-1;
    counts[b]++;
  });
  const labels=counts.map((_,i)=>fmt(min+width*(i+0.5)));
  return { counts, labels };
}

function updateStatCards(params, nomMetrics) {
  document.getElementById("statInitial").textContent = fmt(params.S0);
  document.getElementById("statSimCount").textContent = `${params.nSims.toLocaleString()} simulations`;
  document.getElementById("statMean").textContent = fmt(nomMetrics.mean);
  const growth = ((nomMetrics.mean - params.S0)/params.S0*100).toFixed(1);
  document.getElementById("statMeanDelta").textContent = `+${growth}% total growth`;
  document.getElementById("statMeanDelta").className = "delta up";
  document.getElementById("statVaR").textContent = fmt(nomMetrics.VaR);
  document.getElementById("statVaRDelta").textContent = `at 95% confidence`;
  document.getElementById("statVaRDelta").className = "delta down";
  const probProfit = (100-nomMetrics.probLoss).toFixed(1);
  document.getElementById("statProbProfit").textContent = pct(probProfit);
  document.getElementById("statHorizon").textContent = `${params.years}-year horizon`;
}

function updatePercentiles(m) {
  const html = `
    ${pctRow("Best Case (P95)", m.p95, "green")}
    ${pctRow("Upper Quartile (P75)", m.p75, "blue")}
    ${pctRow("Median (P50)", m.median, "")}
    ${pctRow("Lower Quartile (P25)", m.p25, "yellow")}
    ${pctRow("Worst Case (P5)", m.p5, "red")}
  `;
  document.getElementById("percentileContent").innerHTML = html;
  const profit = (100-m.probLoss);
  document.getElementById("profitBar").style.width = profit+"%";
  document.getElementById("profitPct").textContent = pct(profit);
}

function pctRow(label, val, color) {
  const colors = { green:"#10B981", blue:"#3B82F6", red:"#EF4444", yellow:"#F59E0B", "":"#111827" };
  const bgs    = { green:"#ECFDF5", blue:"#EFF6FF", red:"#FEF2F2", yellow:"#FFFBEB", "":"#F9FAFB" };
  return `
    <div class="pct-row" style="margin-bottom:8px">
      <div><div class="pct-label">${label}</div></div>
      <div style="text-align:right">
        <div class="pct-value" style="color:${colors[color]}">${fmt(val)}</div>
      </div>
    </div>`;
}

function updateMetricsTable(nomM, realM) {
  const set = (id, v) => { const el=document.getElementById(id); if(el) el.textContent=v; };
  set("mMean",    fmt(nomM.mean));
  set("mMedian",  fmt(nomM.median));
  set("mP5",      fmt(nomM.p5));
  set("mP95",     fmt(nomM.p95));
  set("mStd",     fmt(nomM.std));
  set("mProbLoss",pct(nomM.probLoss));
  set("mVaR",     fmt(nomM.VaR));
  set("mRealMean",fmt(realM.mean));
  set("mRealP5",  fmt(realM.p5));
}

function updateInsights(params, nomM) {
  const insights = generateInsights(params, nomM);
  const colors = { warning:["#FFFBEB","#F59E0B"], positive:["#ECFDF5","#10B981"], danger:["#FEF2F2","#EF4444"], neutral:["#EFF6FF","#3B82F6"] };
  const html = insights.map(ins => {
    const [bg] = colors[ins.level] || colors.neutral;
    return `
      <div class="insight-item">
        <div class="insight-icon" style="background:${bg}">${ins.icon}</div>
        <div>
          <div class="insight-text">${ins.text}</div>
          <div class="insight-time">${ins.level.charAt(0).toUpperCase()+ins.level.slice(1)} signal</div>
        </div>
      </div>`;
  }).join("");
  document.getElementById("insightsContainer").innerHTML = html;
}

function generateInsights(params, m) {
  const insights = [];
  const sigPct = params.sigma*100;
  const muPct  = params.mu*100;

  if(sigPct > 25) insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'/></svg>", level:"warning",
    text:`High volatility (${sigPct.toFixed(0)}%) significantly widens the outcome range — your worst-case is ${fmt(m.p5)} vs. a best-case of ${fmt(m.p95)}.` });
  else if(sigPct < 10) insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><polyline points='20 6 9 17 4 12'/></svg>", level:"positive",
    text:`Low volatility (${sigPct.toFixed(0)}%) keeps outcomes tightly clustered with a narrow ${fmt(m.p95-m.p5)} spread between P5 and P95.` });
  else insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><line x1='18' y1='20' x2='18' y2='10'/><line x1='12' y1='20' x2='12' y2='4'/><line x1='6' y1='20' x2='6' y2='14'/></svg>", level:"neutral",
    text:`Moderate volatility (${sigPct.toFixed(0)}%) gives a balanced risk profile. P5–P95 spread: ${fmt(m.p5)} → ${fmt(m.p95)}.` });

  if(params.years >= 20) insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>", level:"positive",
    text:`A ${params.years}-year horizon is a major advantage. Compounding at ${muPct.toFixed(1)}% annually turns small contributions into significant wealth.` });
  else if(params.years <= 5) insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'/><line x1='12' y1='9' x2='12' y2='13'/><line x1='12' y1='17' x2='12.01' y2='17'/></svg>", level:"warning",
    text:`Short ${params.years}-year horizon limits compounding. Volatility has outsized impact — consider a more conservative allocation.` });
  else insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>", level:"neutral",
    text:`${params.years} years is a solid runway. Each additional year roughly multiplies expected value by ${(1+params.mu).toFixed(3)}×.` });

  if(m.probLoss > 30) insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><circle cx='12' cy='12' r='10'/><line x1='15' y1='9' x2='9' y2='15'/><line x1='9' y1='9' x2='15' y2='15'/></svg>", level:"danger",
    text:`${pct(m.probLoss)} chance of ending below ${fmt(params.S0)}. Reducing volatility or extending the horizon would significantly improve this.` });
  else if(m.probLoss < 10) insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><polyline points='20 6 9 17 4 12'/></svg>", level:"positive",
    text:`Only ${pct(m.probLoss)} probability of loss. This is a strong risk-adjusted outlook given the parameters.` });
  else insights.push({ icon:"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><circle cx='12' cy='12' r='10'/><line x1='12' y1='8' x2='12' y2='12'/><line x1='12' y1='16' x2='12.01' y2='16'/></svg>", level:"neutral",
    text:`${pct(m.probLoss)} loss probability. Monthly contributions or slightly lower volatility could push this under 10%.` });

  return insights;
}

function renderPathsChart(data) {
  document.getElementById("pathsEmpty").style.display = "none";
  document.getElementById("pathsChart3D").style.display = "none";
  const canvas = document.getElementById("pathsChart");
  canvas.style.display = "block";
  document.getElementById("legendRow").style.display = "flex";

  const { paths, realPaths, years, nSims } = data;
  const usePaths = currentTab === "nominal" ? paths : realPaths;
  const bands = buildBands(usePaths);

  const sample = usePaths.filter((_,i) => i % Math.ceil(nSims/80) === 0);
  const labels = Array.from({length:usePaths[0].length}, (_,i) => {
    if(i===0) return "Start";
    if(i%12===0) return `Yr ${i/12}`;
    return "";
  });

  const datasets = [
    ...sample.map((p,i) => ({
      data: p,
      borderColor: currentTab==="nominal" ? "rgba(17,24,39,0.06)" : "rgba(59,130,246,0.05)",
      borderWidth: 1,
      pointRadius: 0,
      tension: 0.3,
    })),
    { label:"P95", data: bands.p95, borderColor:"rgba(59,130,246,0.6)",
      backgroundColor:"rgba(59,130,246,0.07)", borderWidth:1.5, pointRadius:0, fill:"+1", tension:0.4 },
    { label:"P75", data: bands.p75, borderColor:"rgba(16,185,129,0.4)",
      backgroundColor:"rgba(16,185,129,0.05)", borderWidth:1, pointRadius:0, fill:"+1", tension:0.4 },
    { label:"Mean", data: bands.mean, borderColor:"#111827",
      backgroundColor:"transparent", borderWidth:2.5, pointRadius:0, tension:0.4 },
    { label:"P25", data: bands.p25, borderColor:"rgba(245,158,11,0.4)",
      backgroundColor:"rgba(245,158,11,0.05)", borderWidth:1, pointRadius:0, fill:"-1", tension:0.4 },
    { label:"P5", data: bands.p5, borderColor:"rgba(239,68,68,0.6)",
      backgroundColor:"rgba(239,68,68,0.07)", borderWidth:1.5, pointRadius:0, fill:false, tension:0.4 },
  ];

  if(pathsChartInst) pathsChartInst.destroy();
  pathsChartInst = new Chart(canvas, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 600, easing:"easeOutQuart" },
      interaction: { mode:"index", intersect:false },
      plugins: {
        legend: { display:false },
        tooltip: {
          filter: d => ["Mean","P95","P5"].includes(d.dataset.label),
          callbacks: {
            label: ctx => `${ctx.dataset.label}: ${fmt(ctx.raw)}`
          }
        }
      },
      scales: {
        x: {
          grid: { display:false },
          ticks: { font:{family:"Plus Jakarta Sans",size:10}, color:"#9CA3AF",
            callback: (v,i,all) => labels[i] || null },
          border: { display:false }
        },
        y: {
          grid: { color:"rgba(0,0,0,0.04)", drawBorder:false },
          ticks: { font:{family:"Plus Jakarta Sans",size:10}, color:"#9CA3AF",
            callback: v => "$"+abbreviate(v) },
          border: { display:false }
        }
      }
    }
  });

  document.getElementById("pathsSubtitle").textContent =
    `${nSims.toLocaleString()} paths over ${years} years — showing mean + P5/P25/P75/P95 bands`;
}

function renderHistogram(finalVals) {
  document.getElementById("histEmpty").style.display = "none";
  const canvas = document.getElementById("histChart");
  canvas.style.display = "block";

  const { counts, labels } = makeHistogram(finalVals, 50);

  if(histChartInst) histChartInst.destroy();
  histChartInst = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data: counts,
        backgroundColor: counts.map((c,i,a) => {
          const norm = i/a.length;
          const r = Math.round(239 - norm*223);
          const g = Math.round(68  + norm*117);
          const b = Math.round(68  + norm*13);
          return `rgba(${r},${g},${b},0.75)`;
        }),
        borderWidth: 0,
        borderRadius: 3,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false},
        tooltip:{ callbacks:{ title: ctx=>ctx[0].label, label: ctx=>`Count: ${ctx.raw}` } } },
      scales: {
        x: { grid:{display:false}, ticks:{display:false}, border:{display:false} },
        y: { grid:{color:"rgba(0,0,0,0.04)"}, ticks:{font:{size:10},color:"#9CA3AF"}, border:{display:false} }
      }
    }
  });
}

function abbreviate(n) {
  if(n>=1e9) return (n/1e9).toFixed(1)+"B";
  if(n>=1e6) return (n/1e6).toFixed(1)+"M";
  if(n>=1e3) return (n/1e3).toFixed(0)+"K";
  return Math.round(n).toString();
}

async function runSimulation(scenario="A") {
  const isA = scenario==="A";
  const btnId = isA ? "runBtn" : "runBtnB";
  const btn = document.getElementById(btnId);

  const prefix = isA ? "" : "b_";
  const params = {
    S0:       parseFloat(document.getElementById(prefix+"initial").value)    || 10000,
    years:    parseInt(document.getElementById(prefix+"years").value)         || 10,
    mu:       parseFloat(document.getElementById(prefix+(isA?"annualReturn":"return")).value)/100 || 0.08,
    sigma:    parseFloat(document.getElementById(prefix+"vol"+(isA?"atility":"")).value)/100      || 0.15,
    inflation:parseFloat(document.getElementById(prefix+"inflation").value)/100                    || 0.03,
    nSims:    parseInt(document.getElementById(prefix+(isA?"nSims":"nSims")).value)               || 1000,
    monthly:  parseFloat(document.getElementById(prefix+"monthly").value)    || 0,
  };

  btn.classList.add("loading");
  btn.innerHTML = `<span class="spin">◌</span> Simulating…`;
  animateProgress(params.nSims);

  await new Promise(r => setTimeout(r, 60));

  let result = null;
  try {
    if(BACKEND_URL) {
      const resp = await fetch(`${BACKEND_URL}/simulate`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({
          initial_investment: params.S0,
          years: params.years,
          annual_return: params.mu*100,
          volatility: params.sigma*100,
          inflation_rate: params.inflation*100,
          num_simulations: params.nSims,
          monthly_contribution: params.monthly
        })
      });
      if(resp.ok) {
        const data = await resp.json();
        if(data.ok) { result = adaptBackendResult(data, params); }
      }
    }
  } catch(e) { /* fall through to JS engine */ }

  if(!result) {
    const sim = runGBM(params);
    const nomMetrics  = computeMetrics(sim.finalNom,  params.S0);
    const realMetrics = computeMetrics(sim.finalReal, params.S0);
    result = {
      paths: sim.paths, realPaths: sim.realPaths,
      finalNom: sim.finalNom, finalReal: sim.finalReal,
      nomMetrics, realMetrics, params
    };
  }

  btn.classList.remove("loading");
  btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg> Run Simulation`;
  if(typeof progressTimer !== 'undefined') clearInterval(progressTimer);
  setProgress(100, params.nSims);

  if(isA) {
    lastResultA = result;
    renderAll(result);
  } else {
    lastResultB = result;
    showComparison();
  }
}

function adaptBackendResult(data, params) {
  const nomM  = data.nom_metrics;
  const realM = data.real_metrics;
  return {
    paths:      data.sampled_paths || [],
    realPaths:  [],
    finalNom:   [], finalReal:[],
    nomMetrics: {
      mean:nomM.mean, median:nomM.median,
      p5:nomM.p5, p25:nomM.p25, p75:nomM.p75, p95:nomM.p95,
      std:nomM.std, probLoss:nomM.prob_loss, VaR:nomM.var_95
    },
    realMetrics: {
      mean:realM.mean, median:realM.median,
      p5:realM.p5, p25:realM.p25, p75:realM.p75, p95:realM.p95,
      std:realM.std, probLoss:realM.prob_loss, VaR:realM.var_95
    },
    histogram: data.histogram,
    insights: data.insights,
    params
  };
}

function renderAll(result) {
  const { paths, realPaths, finalNom, nomMetrics, realMetrics, params } = result;

  updateStatCards(params, nomMetrics);
  updatePercentiles(nomMetrics);
  updateMetricsTable(nomMetrics, realMetrics);

  if (window.currentViewMode === '3d') {
    renderPathsChart3D({ paths, realPaths, years:params.years, nSims:params.nSims });
  } else {
    renderPathsChart({ paths, realPaths, years:params.years, nSims:params.nSims });
  }

  const histData = result.histogram ? result.histogram : makeHistogram(finalNom);
  renderHistogramFromData(histData, params.S0, nomMetrics);

  if(result.insights) {
    const colors={warning:["#FFFBEB"],positive:["#ECFDF5"],danger:["#FEF2F2"],neutral:["#EFF6FF"]};
    const html=result.insights.map(ins=>`
      <div class="insight-item">
        <div class="insight-icon" style="background:${(colors[ins.level]||colors.neutral)[0]}">${ins.icon}</div>
        <div><div class="insight-text">${ins.text}</div>
        <div class="insight-time">${ins.level} signal</div></div>
      </div>`).join("");
    document.getElementById("insightsContainer").innerHTML=html;
  } else {
    updateInsights(params, nomMetrics);
  }

  document.getElementById("rpStatus").textContent = `Last run: ${params.nSims.toLocaleString()} paths, ${params.years}-yr horizon`;
}

function renderHistogramFromData(histData, S0, metrics) {
  document.getElementById("histEmpty").style.display="none";
  const canvas=document.getElementById("histChart");
  canvas.style.display="block";

  const { counts, labels } = histData;

  if(histChartInst) histChartInst.destroy();
  histChartInst = new Chart(canvas, {
    type:"bar",
    data:{
      labels,
      datasets:[{
        data:counts,
        backgroundColor: labels.map(l=>{
          const v=parseFloat(l.replace(/[$,]/g,""));
          return v < S0 ? "rgba(239,68,68,0.65)" : "rgba(16,185,129,0.65)";
        }),
        borderWidth:0, borderRadius:3,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false},
        tooltip:{callbacks:{title:ctx=>ctx[0].label,label:ctx=>`Count: ${ctx.raw}`}}},
      scales:{
        x:{grid:{display:false},ticks:{display:false},border:{display:false}},
        y:{grid:{color:"rgba(0,0,0,0.04)"},ticks:{font:{size:10},color:"#9CA3AF"},border:{display:false}}
      }
    }
  });
}

function showComparison() {
  if(!lastResultA || !lastResultB) return;
  document.getElementById("compareSection").classList.add("visible");
  const mA = lastResultA.nomMetrics;
  const mB = lastResultB.nomMetrics;
  document.getElementById("compareTableA").innerHTML = compareRows(mA, lastResultA.params.S0);
  document.getElementById("compareTableB").innerHTML = compareRows(mB, lastResultB.params.S0);
  document.getElementById("compareSection").scrollIntoView({behavior:"smooth"});
}

function compareRows(m, S0) {
  const rows = [
    ["Mean Portfolio",   fmt(m.mean)],
    ["Median",           fmt(m.median)],
    ["Best Case (P95)",  fmt(m.p95)],
    ["Worst Case (P5)",  fmt(m.p5)],
    ["Std Deviation",    fmt(m.std)],
    ["Prob. of Loss",    pct(m.probLoss)],
    ["VaR (95%)",        fmt(m.VaR)],
    ["Total Growth",     pct((m.mean-S0)/S0*100,1)],
  ];
  return rows.map(([l,v])=>`<tr><td class="m-label">${l}</td><td class="m-value">${v}</td></tr>`).join("");
}

function switchPathTab(tab, el) {
  currentTab = tab;
  const tabs = el.parentElement.querySelectorAll(".chart-tab");
  tabs.forEach(t=>t.classList.remove("active"));
  el.classList.add("active");
  
  if(lastResultA) {
    if (window.currentViewMode === '3d') {
      renderPathsChart3D({
        paths: lastResultA.paths, realPaths: lastResultA.realPaths,
        years: lastResultA.params.years, nSims: lastResultA.params.nSims
      });
    } else {
      renderPathsChart({
        paths: lastResultA.paths, realPaths: lastResultA.realPaths,
        years: lastResultA.params.years, nSims: lastResultA.params.nSims
      });
    }
  }
}

window.currentViewMode = '2d';
function switchViewMode(mode) {
  if (window.currentViewMode === mode) return;
  window.currentViewMode = mode;
  
  document.getElementById('view2dBtn').classList.remove('active');
  document.getElementById('view3dBtn').classList.remove('active');
  document.getElementById('view' + mode + 'Btn').classList.add('active');
  
  if (mode === '2d') {
    document.getElementById('pathsChart').style.display = 'block';
    document.getElementById('pathsChart3D').style.display = 'none';
    document.getElementById('legendRow').style.display = 'flex';
  } else {
    document.getElementById('pathsChart').style.display = 'none';
    document.getElementById('pathsChart3D').style.display = 'block';
    document.getElementById('legendRow').style.display = 'none';
  }

  if (lastResultA) {
    if (mode === '2d') {
      renderPathsChart({
        paths: lastResultA.paths, realPaths: lastResultA.realPaths,
        years: lastResultA.params.years, nSims: lastResultA.params.nSims
      });
    } else {
      renderPathsChart3D({
        paths: lastResultA.paths, realPaths: lastResultA.realPaths,
        years: lastResultA.params.years, nSims: lastResultA.params.nSims
      });
    }
  }
}

function renderPathsChart3D(data) {
  document.getElementById("pathsEmpty").style.display = "none";
  document.getElementById("pathsChart").style.display = "none";
  document.getElementById("legendRow").style.display = "none";
  document.getElementById("pathsChart3D").style.display = "block";
  
  const { paths, realPaths, years, nSims } = data;
  const usePaths = currentTab === "nominal" ? paths : realPaths;
  const steps = usePaths[0].length;
  
  const numBins = 40;
  
  let minVal = Infinity, maxVal = -Infinity;
  for (let p=0; p<nSims; p++) {
    for (let t=0; t<steps; t++) {
      if (usePaths[p][t] < minVal) minVal = usePaths[p][t];
      if (usePaths[p][t] > maxVal) maxVal = usePaths[p][t];
    }
  }
  
  if (maxVal === minVal) maxVal = minVal + 1;
  const binWidth = (maxVal - minVal) / numBins;
  
  const z_data = []; // Y=bins, X=time, Z=density
  const y_data = [];
  
  for (let b=0; b<numBins; b++) {
    y_data.push(minVal + (b + 0.5) * binWidth);
    z_data.push(new Array(steps).fill(0));
  }
  
  for (let p=0; p<nSims; p++) {
    for (let t=0; t<steps; t++) {
      const val = usePaths[p][t];
      let b = Math.floor((val - minVal) / binWidth);
      if (b >= numBins) b = numBins - 1;
      if (b < 0) b = 0;
      z_data[b][t] += 1;
    }
  }
  
  const x_data = Array.from({length: steps}, (_, i) => i/12);
  
  const trace = {
    z: z_data,
    x: x_data,
    y: y_data,
    type: 'surface',
    colorscale: 'Viridis',
    contours: {
        z: { show:true, usecolormap: true, highlightcolor:"#42f462", project:{z: true} }
    }
  };
  
  const layout = {
    autosize: true,
    margin: {l: 0, r: 0, b: 0, t: 0},
    scene: {
      xaxis: {title: 'Time (Years)', titlefont: {color: '#9CA3AF'}, tickfont: {color: '#9CA3AF'}},
      yaxis: {title: 'Portfolio Value', titlefont: {color: '#9CA3AF'}, tickfont: {color: '#9CA3AF'}},
      zaxis: {title: 'Path Density', titlefont: {color: '#9CA3AF'}, tickfont: {color: '#9CA3AF'}},
      camera: { eye: {x: -1.5, y: -1.5, z: 1.2} }
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent'
  };
  
  Plotly.newPlot('pathsChart3D', [trace], layout, {responsive: true});
}

function toggleScenarioB() {
  const panel = document.getElementById("scenarioBPanel");
  const arrow = document.getElementById("scenarioArrow");
  panel.classList.toggle("open");
  arrow.classList.toggle("open");
}

let progressTimer=null;
function animateProgress(nSims) {
  if(progressTimer) clearInterval(progressTimer);
  let pct=0;
  const rate = 100/(nSims/50);
  progressTimer = setInterval(()=>{
    pct = Math.min(pct+rate, 95);
    setProgress(pct, nSims);
    if(pct>=95) clearInterval(progressTimer);
  }, 80);
}
function setProgress(p, nSims) {
  document.getElementById("progressFill").style.width = p+"%";
  document.getElementById("progressPct").textContent  = Math.round(p)+"%";
  document.getElementById("progressLabel").textContent =
    p<100 ? `${Math.round(p/100*nSims).toLocaleString()} paths computed`
           : `${nSims.toLocaleString()} paths complete ✓`;
}

function loadMoreRisky() {
  window._ovTableLimit = (window._ovTableLimit || 10) + 10;
  renderRiskyTable(window._ovFilteredData || window._ovRiskyData);
}

function renderRiskyTable(data) {
  var body = document.getElementById('ovRiskyBody');
  if (!body) return;
  window._ovFilteredData = data;
  if (!window._ovTableLimit) window._ovTableLimit = 10;
  var limit = window._ovTableLimit;
  var html = '';
  data.slice(0, limit).forEach(function(r) {
    var badgeClass = r.label === 'High' ? 'risk-high' : r.label === 'Medium' ? 'risk-medium' : 'risk-low';
    var decClass = r.decision === 'Auto-Approve' ? 'risk-low' : r.decision === 'Auto-Reject' ? 'risk-high' : 'risk-medium';
    html += '<tr><td style="font-weight:600">'+r.name+'</td><td>'+r.sector+'</td><td>'+r.esg_score+'</td><td style="font-weight:700">'+r.risk_score+'</td><td><span class="risk-badge '+badgeClass+'">'+r.label+'</span></td><td><span class="risk-badge '+decClass+'">'+(r.decision||'—')+'</span></td><td style="font-weight:600;color:var(--text)">'+(r.approved_limit ? '$'+r.approved_limit.toLocaleString() : '—')+'</td></tr>';
  });
  body.innerHTML = html;

  var btnContainer = document.getElementById('ovLoadMoreContainer');
  if (btnContainer) {
    btnContainer.style.display = (data.length > limit) ? 'block' : 'none';
  }
}
function sortOvTable(col) {
  if (!window._ovRiskyData) return;
  if (window._ovSortCol === col) window._ovSortAsc = !window._ovSortAsc;
  else { window._ovSortCol = col; window._ovSortAsc = true; }
  var keys = ['name','sector','esg_score','risk_score'];
  var key = keys[col];
  var sorted = (window._ovFilteredData || window._ovRiskyData).slice().sort(function(a,b) {
    var va = a[key], vb = b[key];
    if (typeof va === 'number') return window._ovSortAsc ? va-vb : vb-va;
    return window._ovSortAsc ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
  });
  renderRiskyTable(sorted);
}
function applyOverviewFilters() {
  if (!window._ovRiskyData) return;
  window._ovTableLimit = 10; // Reset limit when filtering
  var sector = document.getElementById('ovFilterSector').value;
  var risk = document.getElementById('ovFilterRisk').value;
  var esgMin = parseInt(document.getElementById('ovFilterEsg').value) || 0;
  document.getElementById('ovEsgRangeVal').textContent = esgMin + ' - 100';
  var filtered = window._ovRiskyData.filter(function(r) {
    if (sector !== 'all' && r.sector !== sector) return false;
    if (risk !== 'all' && r.label !== risk) return false;
    if (r.esg_score < esgMin) return false;
    return true;
  });
  renderRiskyTable(filtered);
}

function goHome() {
  try {
      if (window.parent) {
          window.parent.location.href = '?nav=landing';
      }
  } catch(e) {
      window.location.href = '?nav=landing';
  }
}

var _calDate = new Date();         // Currently viewed month
var _calSelected = new Date();     // Currently selected date

function toggleCalendar() {
  var popup = document.getElementById('calPopup');
  var overlay = document.getElementById('calOverlay');
  if (!popup) return;
  var isOpen = popup.classList.contains('open');
  if (isOpen) {
    popup.classList.remove('open');
    overlay.classList.remove('open');
  } else {
    renderCalendar();
    popup.classList.add('open');
    overlay.classList.add('open');
  }
}

function calNav(dir) {
  _calDate.setMonth(_calDate.getMonth() + dir);
  renderCalendar();
}

function renderCalendar() {
  var months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  var year = _calDate.getFullYear();
  var month = _calDate.getMonth();

  document.getElementById('calMonthYear').textContent = months[month] + ' ' + year;

  var firstDay = new Date(year, month, 1).getDay();
  var daysInMonth = new Date(year, month + 1, 0).getDate();
  var daysInPrev = new Date(year, month, 0).getDate();
  var today = new Date();

  var html = '';

  for (var i = firstDay - 1; i >= 0; i--) {
    html += '<button class="cal-day other-month" onclick="selectCalDay(' + year + ',' + month + ',' + (daysInPrev - i) + ',true)">' + (daysInPrev - i) + '</button>';
  }

  for (var d = 1; d <= daysInMonth; d++) {
    var classes = 'cal-day';
    if (d === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
      classes += ' today';
    }
    if (d === _calSelected.getDate() && month === _calSelected.getMonth() && year === _calSelected.getFullYear()) {
      classes += ' selected';
    }
    html += '<button class="' + classes + '" onclick="selectCalDay(' + year + ',' + month + ',' + d + ')">' + d + '</button>';
  }

  var totalCells = firstDay + daysInMonth;
  var remaining = (7 - (totalCells % 7)) % 7;
  for (var n = 1; n <= remaining; n++) {
    html += '<button class="cal-day other-month" onclick="selectCalDay(' + year + ',' + (month+1) + ',' + n + ',true)">' + n + '</button>';
  }

  document.getElementById('calDays').innerHTML = html;
}

function selectCalDay(y, m, d, isOtherMonth) {
  _calSelected = new Date(y, m, d);
  if (isOtherMonth) {
    _calDate = new Date(y, m, 1);
  }

  var opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  var dateStr = _calSelected.toLocaleDateString('en-US', opts);
  var el = document.getElementById('dateText');
  if (el) el.textContent = dateStr;

  var greetEl = document.getElementById('greetingText');

  var ovDateEl = document.getElementById('ovDate');
  if (ovDateEl) ovDateEl.textContent = dateStr;

  applyDateDataShift(_calSelected);

  toggleCalendar();
  renderCalendar();
}

function applyDateDataShift(selectedDate) {
  var dayOfYear = Math.floor((selectedDate - new Date(selectedDate.getFullYear(), 0, 0)) / 86400000);
  var seed = dayOfYear * 7 + selectedDate.getFullYear();

  function seededRand(s) { s = (s * 9301 + 49297) % 233280; return s / 233280; }

  var cards = document.querySelectorAll('.stat-card');
  cards.forEach(function(card, i) {
    card.classList.remove('stat-refresh');
    void card.offsetWidth; // Force reflow to restart animation
    card.classList.add('stat-refresh');

    var valEl = card.querySelector('.stat-value');
    if (valEl) {
      var original = valEl.getAttribute('data-original');
      if (!original) {
        original = valEl.textContent;
        valEl.setAttribute('data-original', original);
      }

      var shift = seededRand(seed + i);
      var text = original;

      if (text.indexOf('$') === 0) {
        var num = parseFloat(text.replace(/[$,]/g, ''));
        if (!isNaN(num)) {
          var factor = 0.85 + shift * 0.3; // ±15% variation
          var newVal = Math.round(num * factor);
          valEl.textContent = '$' + newVal.toLocaleString();
        }
      }
      else if (text.indexOf('%') > -1) {
        var pct = parseFloat(text.replace('%', ''));
        if (!isNaN(pct)) {
          var newPct = Math.max(60, Math.min(99.9, pct + (shift - 0.5) * 10));
          valEl.textContent = newPct.toFixed(1) + '%';
        }
      }
    }
  });

  var deltas = document.querySelectorAll('.delta');
  deltas.forEach(function(delta, i) {
    var r = seededRand(seed + i + 100);
    if (r > 0.5) {
      delta.className = 'delta up';
      delta.innerHTML = '↑ +' + (r * 8).toFixed(1) + '%';
    } else {
      delta.className = 'delta down';
      delta.innerHTML = '↓ -' + ((1 - r) * 5).toFixed(1) + '%';
    }
  });
}

function toggleSimSection() {
  var sec = document.getElementById('pdSimSection');
  var grid = document.getElementById('pdGrid');
  var rp = document.querySelector('.right-panel');
  if (!sec) return;
  
  var isOpen = sec.classList.contains('open');
  if (isOpen) {
    sec.classList.remove('open');
    if (grid) grid.style.display = 'grid';
    if (rp) rp.style.display = 'none';
  } else {
    sec.classList.add('open');
    if (grid) grid.style.display = 'none';
    if (rp) rp.style.display = 'flex';
    if (!lastResultA) setTimeout(function(){ runSimulation('A'); }, 300);
  }
}

function renderPDCards() {
  var D = (typeof DASHBOARD_DATA !== 'undefined') ? DASHBOARD_DATA : {};
  
  var highR = 0, modR = 0, lowR = 0;
  if (D.risk_distribution) {
    highR = D.risk_distribution.high;
    modR = D.risk_distribution.medium;
    lowR = D.risk_distribution.low;
  } else if (D.risky_entities) {
    D.risky_entities.forEach(function(e) {
      if (e.label === 'High') highR++;
      else if (e.label === 'Medium') modR++;
      else lowR++;
    });
  } else {
    highR = 14; modR = 64; lowR = 32;
  }
  setText('pdHighCount', highR);
  setText('pdModCount', modR);
  setText('pdLowCount', lowR);
  
  var ctx = document.getElementById('pdDonutChart');
  if (ctx) new Chart(ctx, {
    type:'doughnut',
    data:{labels:['High Risk','Moderate','Low Risk'],datasets:[{data:[highR,modR,lowR],backgroundColor:['#F59E0B','#3B82F6','#10B981'],borderWidth:0,hoverOffset:6}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:'68%',plugins:{legend:{display:false}}}
  });
  
  var riskLabels = ['Jan','Feb','Mar','Apr','May','Jun'];
  var riskData = [20,22,19,24,21,23];
  var esgData = [45,48,50,52,53,55];
  if (D.risk_timeseries) { riskLabels = D.risk_timeseries.labels; riskData = D.risk_timeseries.values; }
  if (D.esg_trend) { esgData = D.esg_trend.data; riskLabels = D.esg_trend.labels; }
  if (D.ai_risk_score) setText('pdRiskVal', D.ai_risk_score);
  if (D.avg_esg) setText('pdEsgVal', D.avg_esg);
  
  var ctx2 = document.getElementById('pdAreaChart');
  if (ctx2) new Chart(ctx2, {
    type:'line',
    data:{labels:riskLabels,datasets:[
      {label:'Risk',data:riskData,borderColor:'#3B82F6',backgroundColor:'rgba(59,130,246,0.08)',borderWidth:2,pointRadius:3,pointBackgroundColor:'#fff',pointBorderColor:'#3B82F6',fill:true,tension:0.4},
      {label:'ESG',data:esgData,borderColor:'#10B981',backgroundColor:'rgba(16,185,129,0.08)',borderWidth:2,pointRadius:3,pointBackgroundColor:'#fff',pointBorderColor:'#10B981',fill:true,tension:0.4}
    ]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'rgba(0,0,0,0.04)'},beginAtZero:true}}}
  });
  
  var crit=0,high=0,mod=0,low=0,rev=0;
  if (D.risk_buckets) {
    crit = D.risk_buckets.critical;
    high = D.risk_buckets.high;
    mod = D.risk_buckets.moderate;
    low = D.risk_buckets.low;
    rev = D.risk_buckets.review;
  } else if (D.risky_entities) {
    D.risky_entities.forEach(function(e){
      var s = e.risk_score;
      if(s>=85) crit++;
      else if(s>=70) high++;
      else if(s>=50) mod++;
      else if(s>=30) low++;
      else rev++;
    });
  }
  var total = (crit+high+mod+low+rev) || 1;
  setText('pdCritCnt',crit); setText('pdHighCnt2',high); setText('pdModCnt2',mod); setText('pdLowCnt2',low); setText('pdRevCnt',rev);
  
  var max_val = Math.max(crit, high, mod, low, rev) || 1;
  var rows = document.querySelectorAll('.pd-invoice-bar > div');
  if(rows.length>=5){
    rows[0].style.width=(crit/max_val*100)+'%';
    rows[1].style.width=(high/max_val*100)+'%';
    rows[2].style.width=(mod/max_val*100)+'%';
    rows[3].style.width=(low/max_val*100)+'%';
    rows[4].style.width=(rev/max_val*100)+'%';
  }
  
  var now = new Date();
  var dateEl = document.getElementById('dateText');
  if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US',{weekday:'long',year:'numeric',month:'long',day:'numeric'});
}

window.addEventListener('load', function() {
  setTimeout(renderPDCards, 200);
});



(function() {
  var _origToggle = window.toggleCalendar;
  window.toggleCalendar = function() {
    var popup = document.getElementById('calPopup');
    var btn = document.getElementById('calendarBtn');
    if (popup && btn && !popup.classList.contains('open')) {
      var rect = btn.getBoundingClientRect();
      popup.style.top = (rect.bottom + 8) + 'px';
      popup.style.right = (window.innerWidth - rect.right) + 'px';
    }
    _origToggle();
  };
  function initPDSim() {
  }

  function updateSimulator() {
    var inc = parseFloat(document.getElementById('wiIncome').value);
    var amt = parseFloat(document.getElementById('wiAmount').value);
    var pd = parseFloat(document.getElementById('wiPD').value);
    
    setText('wiIncomeVal', '$' + inc.toLocaleString());
    setText('wiAmountVal', '$' + amt.toLocaleString());
    setText('wiPDVal', pd + '%');
    
    var pd_ratio = pd / 100.0;
    var base_rate = 5.5;
    var max_ltv = 0.30;
    
    var decision = "";
    var limit = 0;
    var rate = 0;
    var badgeClass = "";
    
    if (pd_ratio < 0.10) {
      decision = "Auto-Approve";
      limit = Math.min(inc * max_ltv, amt);
      rate = base_rate + (pd_ratio * 20);
      badgeClass = "approve";
    } else if (pd_ratio > 0.40) {
      decision = "Auto-Reject";
      limit = 0;
      rate = 0;
      badgeClass = "reject";
    } else {
      decision = "Manual Review";
      limit = Math.min(inc * (max_ltv - 0.1), amt);
      rate = base_rate + (pd_ratio * 35);
      badgeClass = "review";
    }
    
    setText('wiDecision', decision);
    var badge = document.getElementById('wiDecisionBadge');
    if (badge) { badge.className = 'wi-decision-badge ' + badgeClass; }
    
    setText('wiLimit', limit > 0 ? '$' + Math.round(limit).toLocaleString() : '—');
    setText('wiRate', rate === 0 ? "—" : rate.toFixed(2) + '%');
    
    if (limit > 0 && rate > 0) {
      var mr = (rate / 100) / 12;
      var n = 60;
      var monthly = limit * (mr * Math.pow(1 + mr, n)) / (Math.pow(1 + mr, n) - 1);
      setText('wiMonthly', '$' + Math.round(monthly).toLocaleString());
    } else {
      setText('wiMonthly', '—');
    }
    
    var gaugeArc = document.getElementById('wiGaugeArc');
    var gaugePct = document.getElementById('wiGaugePct');
    if (gaugeArc) {
      var fillLen = (pd / 100) * 204;
      gaugeArc.setAttribute('stroke-dashoffset', 204 - fillLen);
    }
    if (gaugePct) { gaugePct.textContent = pd + '%'; }
    
    var tierFill = document.getElementById('wiTierFill');
    if (tierFill) {
      tierFill.style.width = pd + '%';
      if (pd < 10) tierFill.style.background = 'linear-gradient(90deg,#10B981,#34D399)';
      else if (pd < 25) tierFill.style.background = 'linear-gradient(90deg,#10B981,#3B82F6)';
      else if (pd < 40) tierFill.style.background = 'linear-gradient(90deg,#3B82F6,#F59E0B)';
      else if (pd < 60) tierFill.style.background = 'linear-gradient(90deg,#F59E0B,#EF4444)';
      else tierFill.style.background = 'linear-gradient(90deg,#EF4444,#DC2626)';
    }
  }
  window.updateSimulator = updateSimulator;
  
  document.addEventListener("DOMContentLoaded", function() {
    if(document.getElementById('wiIncome')) updateSimulator();
  });
})();

/* Topbar Functionalities */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  
  const toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.innerHTML = '<div class="toast-icon">' + (type === 'success' ? '?' : 'i') + '</div><div>' + message + '</div>';
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function filterData(btn, timeframe) {
  btn.parentElement.querySelectorAll('.pd-tab').forEach(t => t.classList.remove('pd-tab-active'));
  btn.classList.add('pd-tab-active');
  showToast('Loading ' + timeframe + ' analytics...', 'info');
  
  const mainGrid = document.getElementById('pdGrid');
  if(mainGrid) {
    mainGrid.style.opacity = '0.4';
    mainGrid.style.pointerEvents = 'none';
    
    setTimeout(() => {
      // Actually change the dashboard data based on timeframe
      const portEl = document.getElementById('ovPortfolio');
      const riskEl = document.getElementById('ovRiskScore');
      const esgEl = document.getElementById('ovESG');
      const highRiskEl = document.getElementById('ovHighRiskPct');
      
      if (timeframe === 'Today') {
        if(portEl) portEl.textContent = '$1.11B';
        if(riskEl) riskEl.textContent = '42';
        if(esgEl) esgEl.textContent = '65.2';
        if(highRiskEl) highRiskEl.textContent = '8.1%';
      } else if (timeframe === 'This Week') {
        if(portEl) portEl.textContent = '$1.13B';
        if(riskEl) riskEl.textContent = '43';
        if(esgEl) esgEl.textContent = '64.8';
        if(highRiskEl) highRiskEl.textContent = '8.5%';
      } else if (timeframe === 'This Month') {
        if(portEl) portEl.textContent = '$1.15B';
        if(riskEl) riskEl.textContent = '45';
        if(esgEl) esgEl.textContent = '62.4';
        if(highRiskEl) highRiskEl.textContent = '9.2%';
      }

      mainGrid.style.opacity = '1';
      mainGrid.style.pointerEvents = 'auto';
      showToast(timeframe + ' analytics loaded successfully', 'success');
    }, 800);
  }
}

function generateReport() {
  showToast('Preparing PDF Report...', 'info');
  setTimeout(() => {
    window.print(); // Triggers the browser's native Save to PDF dialog
    showToast('Report generated!', 'success');
  }, 1000);
}

function readNotifications() {
  const dot = document.getElementById('notifDot');
  if(dot && dot.style.display !== 'none') {
    dot.style.display = 'none';
    showToast('You have 3 unread alerts', 'info');
  } else {
    showToast('No new notifications', 'info');
  }
}

let isBookmarked = false;
function toggleBookmark() {
  isBookmarked = !isBookmarked;
  const icon = document.getElementById('bookmarkIcon');
  if(icon) {
    icon.setAttribute('fill', isBookmarked ? 'currentColor' : 'none');
  }
  showToast(isBookmarked ? 'Dashboard view bookmarked' : 'Bookmark removed', 'success');
}
