"""
plotting the mesh segments as inputted and after resolve_mesh_segment function is applied
which includes these 3 functions:
    1.    _resolve_mesh_segments_overlap_region()
    2.    _resolve_mesh_segments_narrow_region()
    3.    _resolve_mesh_segments_ds()
"""
from matplotlib import pyplot as plt


def plot_segments(inputed_mesh, adjusted_mesh):
    fig, axs = plt.subplots(3)
    '''
    plot the input segments- given by the user
    '''

    for segments in inputed_mesh['segment_list']:
        axs[0].hlines(segments['ds0'], segments['s0'], segments['s1'], linewidth=3)
        axs[0].axvline(x=segments['s1'], dashes=[6, 2], color='gray')
        axs[0].axvline(x=segments['s0'], dashes=[6, 2], color='gray')
    axs[0].set_title('Input segments')
    axs[0].set(xlabel=' \u03B8 ', ylabel='\u0394 \u03B8')

    '''
    plot the output segments- after applying the function called "resolve_mesh_segments()"
    '''

    for segments in adjusted_mesh['segment_list']:
        axs[1].hlines(max(segments['ds0'], segments['ds1']), segments['s0'], segments['s1'], linewidth=3)
        axs[1].axvline(x=segments['s1'], dashes=[6, 2], color='gray')
        axs[1].axvline(x=segments['s0'], dashes=[6, 2], color='gray')
    axs[1].set_title('_resolve_mesh_segments_overlap_region()')
    axs[1].set(xlabel=' \u03B8 ', ylabel='\u0394 \u03B8')

    '''
    plot the output segments- after applying the function called "resolve_mesh_segments()"- 
    linear line connecting 2 points
    
    '''

    for segments in adjusted_mesh['segment_list']:
        axs[2].plot([segments['s1'], segments['s0']], [segments['ds1'], segments['ds0']], linewidth=3, color='k')
        axs[2].axvline(x=segments['s1'], dashes=[6, 2], color='gray')
        axs[2].axvline(x=segments['s0'], dashes=[6, 2], color='gray')
        axs[2].set_title('_resolve_mesh_segments_ds()')
        axs[2].set(xlabel=' \u03B8 ', ylabel='\u0394 \u03B8')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    from tests.ar_test import *

    my_mesh = get_mesh_phi_1().json_dict()
    adjusted_mesh = adjust__mesh_phi_1().json_dict()
    plot_segments(my_mesh, adjusted_mesh)
