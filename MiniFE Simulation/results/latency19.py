import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# IEEE Formatting
plt.rcParams.update({
    'font.family': 'serif', 'font.serif': ['Times New Roman'],
    'font.size': 10, 'axes.labelsize': 12, 'legend.fontsize': 10,
    'figure.dpi': 300
})

# Your data
patterns = ['Allreduce', 'Allgather', 'Bcast', 'Barrier']
topologies = ['Mesh', 'Torus', 'Dragonfly', 'FatTree']
node_counts = [4, 16, 64, 256, 1024]

# Hopcount data
hopcount_data = {
    'Mesh': {
        'Allreduce': [3.33, 4.67, 7.33, 12.67, 23.33],
        'Allgather': [3.33, 4.67, 7.33, 12.67, 23.33],
        'Bcast':[3.33, 4.67, 7.33, 12.67, 23.33],    
        'Barrier':[6.5, 16.12, 31.03, 56.51, 103.25] 
    },
    'Torus': {
        'Allreduce': [3.33, 4.13, 6.06, 10.03, 18.02],
        'Allgather': [3.33, 4.13, 6.06, 10.03, 18.02],
        'Bcast':[3.33, 4.13, 6.06, 10.03, 18.02],
        'Barrier': [6.5, 14.75, 26.88, 46.94, 82.97]  
    },
    'Dragonfly': {
        'Allreduce': [3.67, 4.07, 4.52, 4.76, 4.88],
        'Allgather': [3.67, 4.07, 4.52, 4.76, 4.88],
        'Bcast': [3.67, 4.07, 4.52, 4.76, 4.88],
        'Barrier': [6.0, 15.75, 23.88, 31.94, 39.97] 
    },
    'FatTree': {
        'Allreduce': [4.33, 6.47, 6.87, 6.86, 6.96],
        'Allgather': [4.33, 6.47, 6.87, 6.86, 6.96],
        'Bcast': [4.33, 6.47, 6.87, 6.86, 6.96],
        'Barrier':[9.0, 24.5, 38.5, 47.38, 61.38]  
    }
}

# Latency data 
latency_data = {
    'Allreduce': {
        'Mesh': [3.761, 7.806, 13.109, 21.817, 36.855],
        'Torus': [3.761, 7.806, 12.946, 20.931, 34.265],
        'Dragonfly': [3.761, 7.975, 12.025, 16.437, 20.975],
        'FatTree': [3.761, 8.491, 13.224, 17.270, 22.154]
    },
    'Bcast': {
        'Mesh': [0.440, 0.570, 0.570, 0.570, 0.570],
        'Torus': [0.440, 0.570, 0.570, 0.570, 1.893],
        'Dragonfly': [0.440, 0.570, 0.570, 0.570, 0.571],
        'FatTree': [0.440, 0.570, 0.570, 0.570, 0.570]
    },
    'Allgather': {
        'Mesh': [3.817, 5.411, 8.036, 11.495, 18.572],
        'Torus': [3.817, 6.236, 9.137, 12.016, 17.705],
        'Dragonfly': [3.817, 5.211, 7.813, 10.857, 18.819],
        'FatTree': [3.768, 6.789, 9.746, 10.818, 14.694]
    },
    'Barrier': {
        'Mesh': [3.753, 7.815, 13.146, 21.895, 36.960],
        'Torus': [3.753, 7.797, 12.937, 20.929, 34.266],
        'Dragonfly': [3.753, 7.997, 12.033, 16.438, 20.965],
        'FatTree': [3.753, 8.483, 13.212, 17.291, 22.156]
    }
}

def create_individual_topology_plots():
    """Create separate hopcount vs latency plots for each topology"""
    
    colors = {'Allreduce': '#1f77b4', 'Allgather': '#ff7f0e', 
              'Bcast': '#2ca02c', 'Barrier': '#d62728'}
    markers = {'Allreduce': 'o', 'Allgather': 's', 'Bcast': '^', 'Barrier': 'D'}
    
    correlation_results = []
    
    for topology in topologies:
        fig, ax = plt.subplots(figsize=(4, 3))
        
        # Plot each pattern for this topology
        for pattern in patterns:
            if pattern in hopcount_data[topology]:
                hopcounts = hopcount_data[topology][pattern]
                latencies = latency_data[pattern][topology]
                
                # Match array lengths
                n_points = min(len(hopcounts), len(latencies))
                hopcounts_plot = hopcounts[:n_points]
                latencies_plot = latencies[:n_points]
                
                # Calculate correlation and regression
                if len(hopcounts_plot) > 1:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(hopcounts_plot, latencies_plot)
                    r_squared = r_value ** 2
                    correlation_results.append({
                        'topology': topology,
                        'pattern': pattern,
                        'r_squared': r_squared,
                        'slope': slope,
                        'p_value': p_value
                    })
                    
                    # Plot scatter points
                    ax.scatter(hopcounts_plot, latencies_plot,
                             marker=markers[pattern], s=25,
                             color=colors[pattern], alpha=0.8,
                             label=f'{pattern} (R² = {r_squared:.3f})')
                    
                    # Plot trend line
                    x_line = np.linspace(min(hopcounts_plot), max(hopcounts_plot), 100)
                    y_line = slope * x_line + intercept
                    ax.plot(x_line, y_line, color=colors[pattern], 
                           alpha=0.6, linewidth=2, linestyle='-')
        
        # Customize the plot
        ax.set_xlabel('Average Hopcount',  fontsize=16)
        ax.set_ylabel('Latency (μs)',  fontsize=16)
        ax.set_title(f' {topology} Topology', 
                    fontweight='bold', fontsize=16)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best',fontsize=10)
        
        # Add statistical summary
        topology_correlations = [r for r in correlation_results if r['topology'] == topology]
        if topology_correlations:
            avg_r2 = np.mean([r['r_squared'] for r in topology_correlations])
            ax.text(0.02, 0.98, f'Avg R² = {avg_r2:.3f}', 
                   transform=ax.transAxes, fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
                    va='top')
        
        plt.tight_layout()
        
        # Save individual plot
        filename = f'hopcount_latency_{topology.lower()}.pdf'
        fig.savefig(filename, bbox_inches='tight', dpi=300)
        print(f"Saved: {filename}")
        
        plt.show()
    
    return correlation_results

# Generate individual plots
correlation_stats = create_individual_topology_plots()

# Print correlation statistics
print("\nCORRELATION STATISTICS:")
print("="*60)
print(f"{'Topology':<12} {'Pattern':<12} {'R²':<8} {'Slope':<10} {'p-value':<10}")
print("-"*60)
for stats in correlation_stats:
    print(f"{stats['topology']:<12} {stats['pattern']:<12} {stats['r_squared']:.3f}    {stats['slope']:.3f}      {stats['p_value']:.4f}")

# Calculate overall statistics
topology_avg_r2 = {}
for topology in topologies:
    topology_stats = [s for s in correlation_stats if s['topology'] == topology]
    topology_avg_r2[topology] = np.mean([s['r_squared'] for s in topology_stats])

print("\nOVERALL CORRELATION BY TOPOLOGY:")
print("="*40)
for topology, avg_r2 in topology_avg_r2.items():
    print(f"{topology:<12}: R² = {avg_r2:.3f} (explains {avg_r2*100:.1f}% of variance)")

overall_avg_r2 = np.mean([s['r_squared'] for s in correlation_stats])
print(f"\nOverall Average R²: {overall_avg_r2:.3f}")
print(f"Hopcount explains {(overall_avg_r2*100):.1f}% of latency variance across all topologies")
print("="*60)