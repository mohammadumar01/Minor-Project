import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# IEEE Formatting
plt.rcParams.update({
    'font.family': 'serif', 'font.serif': ['Times New Roman'],
    'font.size': 10, 'axes.labelsize': 12, 'legend.fontsize': 10,
    'figure.dpi': 300
})

# MinimMD Mesh3D Data
mesh3d_grid_sizes = ['2x2x4', '4x4x2', '4x4x4', '8x8x2', '8x8x4', '8x8x8', '16x16x4']

mesh3d_latency = {
    'Allreduce': [7.082, 8.962, 11.215, 14.434, 16.805, 19.899, 24.906],
    'Barrier': [7.178, 9.075, 11.354, 14.610, 17.013, 20.151, 25.221]
}

mesh3d_hopcount = {
    'Allreduce': [4.4, 5.097, 5.81, 7.795, 8.525, 9.89, 13.887],
    'Barrier': [15.125, 20.062, 25.031, 35.016, 40.008, 47.504, 65.502]
}

# MinimMD Torus3D Data
torus3d_latency = {
    'Allreduce': [7.213, 8.962, 11.439, 14.488, 17.176, 19.982, 25.307],
    'Barrier': [7.312, 9.075, 11.582, 14.666, 17.389, 20.233, 25.624]
}

torus3d_hopcount = {
    'Allreduce': [4.133, 4.581, 5.048, 6.535, 7.02, 8.012, 11.009],
    'Barrier': [14.25, 18.688, 22.688, 30.859, 34.859, 40.859, 54.934]
}

def create_mesh3d_plot():
    """Create hopcount vs latency correlation plot for MinimMD Mesh3D"""
    fig, ax = plt.subplots(figsize=(4, 3))
    
    colors = {'Allreduce': '#1f77b4', 'Barrier': '#d62728'}
    markers = {'Allreduce': 'o', 'Barrier': 's'}
    
    correlation_results = []
    
    # Plot each pattern for Mesh3D
    for pattern in ['Allreduce', 'Barrier']:
        hopcounts = mesh3d_hopcount[pattern]
        latencies = mesh3d_latency[pattern]
        
        # Calculate correlation and regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(hopcounts, latencies)
        r_squared = r_value ** 2
        
        correlation_results.append({
            'pattern': pattern,
            'r_squared': r_squared,
            'slope': slope,
            'intercept': intercept,
            'p_value': p_value
        })
        
        # Plot scatter points with grid size labels
        scatter = ax.scatter(hopcounts, latencies,
                           marker=markers[pattern], s=25,
                           color=colors[pattern], alpha=0.8,
                           label=f'{pattern} (R² = {r_squared:.3f})')
        
        # # Add grid size labels to points
        # for i, (hc, lat, grid) in enumerate(zip(hopcounts, latencies, mesh3d_grid_sizes)):
        #     ax.annotate(grid, (hc, lat), 
        #                xytext=(5, 5), textcoords='offset points',
        #                fontsize=8, alpha=0.7)
        
        # Plot trend line
        x_line = np.linspace(min(hopcounts), max(hopcounts), 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, color=colors[pattern], 
               alpha=0.6, linewidth=2, linestyle='-')
    
    # Customize the plot
    ax.set_xlabel('Average Hopcount', fontsize=16)
    ax.set_ylabel('Latency (μs)', fontsize=16)
    ax.set_title('Mesh3D Topology', 
                fontweight='bold', fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best',fontsize=10)
    
    # Add statistical summary
    avg_r2 = np.mean([r['r_squared'] for r in correlation_results])
   
    
    
    ax.text(0.02, 0.98,  f'Avg R² = {avg_r2:.3f}', transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    return fig, correlation_results

def create_torus3d_plot():
    """Create hopcount vs latency correlation plot for MinimMD Torus3D"""
    fig, ax = plt.subplots(figsize=(4,3))
    
    colors = {'Allreduce': '#2ca02c', 'Barrier': '#ff7f0e'}  # Different colors for Torus3D
    markers = {'Allreduce': 'o', 'Barrier': 's'}
    
    correlation_results = []
    
    # Plot each pattern for Torus3D
    for pattern in ['Allreduce', 'Barrier']:
        hopcounts = torus3d_hopcount[pattern]
        latencies = torus3d_latency[pattern]
        
        # Calculate correlation and regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(hopcounts, latencies)
        r_squared = r_value ** 2
        
        correlation_results.append({
            'pattern': pattern,
            'r_squared': r_squared,
            'slope': slope,
            'intercept': intercept,
            'p_value': p_value
        })
        
        # Plot scatter points with grid size labels
        scatter = ax.scatter(hopcounts, latencies,
                           marker=markers[pattern], s=25,
                           color=colors[pattern], alpha=0.8,
                           label=f'{pattern} (R² = {r_squared:.3f})')
        
        # # Add grid size labels to points
        # for i, (hc, lat, grid) in enumerate(zip(hopcounts, latencies, mesh3d_grid_sizes)):
        #     ax.annotate(grid, (hc, lat), 
        #                xytext=(5, 5), textcoords='offset points',
        #                fontsize=8, alpha=0.7)
        
        # Plot trend line
        x_line = np.linspace(min(hopcounts), max(hopcounts), 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, color=colors[pattern], 
               alpha=0.6, linewidth=2, linestyle='-')
    
    # Customize the plot
    ax.set_xlabel('Average Hopcount',  fontsize=16)
    ax.set_ylabel('Latency (μs)',  fontsize=16)
    ax.set_title('Torus3D Topology', 
                fontweight='bold', fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best',fontsize=10)
    
    # Add statistical summary
    avg_r2 = np.mean([r['r_squared'] for r in correlation_results])
    
   
    
    ax.text(0.02, 0.98,f'Avg R² = {avg_r2:.3f}', transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    return fig, correlation_results

# Generate separate plots
print("Generating Separate MinimMD Correlation Plots...")
print("="*50)

# Mesh3D plot
fig_mesh, mesh_stats = create_mesh3d_plot()
fig_mesh.savefig('mesh3d_hopcount_latency_correlation.pdf', bbox_inches='tight', dpi=300)
print("Saved: mesh3d_hopcount_latency_correlation.pdf")

# Torus3D plot
fig_torus, torus_stats = create_torus3d_plot()
fig_torus.savefig('torus3d_hopcount_latency_correlation.pdf', bbox_inches='tight', dpi=300)
print("Saved: torus3d_hopcount_latency_correlation.pdf")

# Print detailed statistics for each topology separately
print("\n" + "="*60)
print("MESH3D CORRELATION STATISTICS:")
print("="*60)
print(f"{'Pattern':<12} {'R²':<8} {'Slope':<10} {'Intercept':<12} {'p-value':<10}")
print("-"*60)
for stats in mesh_stats:
    print(f"{stats['pattern']:<12} {stats['r_squared']:.3f}    {stats['slope']:.3f}      {stats['intercept']:.3f}       {stats['p_value']:.6f}")

mesh_avg_r2 = np.mean([r['r_squared'] for r in mesh_stats])
print(f"\nMesh3D Average R²: {mesh_avg_r2:.3f}")
print(f"Hopcount explains {mesh_avg_r2*100:.1f}% of latency variance in Mesh3D")

print("\n" + "="*60)
print("TORUS3D CORRELATION STATISTICS:")
print("="*60)
print(f"{'Pattern':<12} {'R²':<8} {'Slope':<10} {'Intercept':<12} {'p-value':<10}")
print("-"*60)
for stats in torus_stats:
    print(f"{stats['pattern']:<12} {stats['r_squared']:.3f}    {stats['slope']:.3f}      {stats['intercept']:.3f}       {stats['p_value']:.6f}")

torus_avg_r2 = np.mean([r['r_squared'] for r in torus_stats])
print(f"\nTorus3D Avg R²: {torus_avg_r2:.3f}")
print(f"Hopcount explains {torus_avg_r2*100:.1f}% of latency variance in Torus3D")

print("\n" + "="*60)
print("KEY OBSERVATIONS:")
print("="*60)
print("1. Both topologies show strong correlation between hopcount and latency")
print("2. Barrier operations have higher hopcounts but similar correlation strength")
print("3. Torus3D generally shows slightly lower hopcounts due to wrap-around links")
print("4. R² values > 0.95 indicate hopcount is a strong predictor of latency")

plt.show()