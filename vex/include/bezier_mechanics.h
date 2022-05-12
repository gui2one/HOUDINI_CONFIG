
#ifndef __bezier_mechanics__
#define __bezier_mechanics__

function vector bezier_sample(vector p1; vector p2; vector p3; vector p4; float t){

    vector result = set(0.0,0.0,0.0);


    vector p12 = lerp(p1, p2, t);
    vector p23 = lerp(p2, p3, t);
    vector p34 = lerp(p3, p4, t);

    vector p_111 = lerp(p12, p23, t);
    vector p_222 = lerp(p23, p34, t);

    vector p_1111 = lerp(p_111, p_222, t);
    return p_1111; 
}

function vector[] bezier_samples(vector p1; vector p2; vector p3; vector p4; int num_samples; float min_t; float max_t; )
{
    vector samples[] = {};
    for(int i= 0; i< num_samples; i++){
        float t = float(1.0 / (num_samples-1)) * i;
        float fitted = fit(t, 0, 1, min_t, max_t);
        append(samples, bezier_sample(p1, p2, p3, p4, fitted));
    }
    return samples;
}
#endif