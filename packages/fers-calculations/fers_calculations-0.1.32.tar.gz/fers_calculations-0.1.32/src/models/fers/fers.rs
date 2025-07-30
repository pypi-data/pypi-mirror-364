
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use std::collections::{BTreeMap, HashMap};
use nalgebra::{DMatrix, DVector};
use std::collections::HashSet;
// use csv::Writer;
// use std::error::Error;
use crate::models::members::{material::Material, section::Section, memberhinge::MemberHinge, shapepath::ShapePath};
use crate::models::members::memberset::MemberSet;
use crate::models::loads::loadcase::LoadCase;
use crate::models::loads::loadcombination::LoadCombination;
use crate::models::imperfections::imperfectioncase::ImperfectionCase;
use crate::models::results::displacement::NodeDisplacement;
use crate::models::results::forces::{MemberForce, NodeForces, ReactionForce};
use crate::models::results::memberresultmap::MemberResultMap;
use crate::models::results::resultbundle::ResultsBundle;
use crate::models::results::results::{ResultType, Results};
use crate::models::results::resultssummary::ResultsSummary;
use crate::models::settings::settings::Settings;
use crate::models::supports::nodalsupport::NodalSupport;

use crate::functions::load_assembler::{assemble_nodal_loads, assemble_nodal_moments, assemble_distributed_loads};


#[derive(Serialize, Deserialize, ToSchema, Debug)]
pub struct FERS {
    pub member_sets: Vec<MemberSet>,
    pub load_cases: Vec<LoadCase>,
    pub load_combinations: Vec<LoadCombination>,
    pub imperfection_cases: Vec<ImperfectionCase>,
    pub settings: Settings, 
    pub results: Option<ResultsBundle>,  
    pub memberhinges: Option<Vec<MemberHinge>>,
    pub materials: Vec<Material>,
    pub sections: Vec<Section>,
    pub nodal_supports: Vec<NodalSupport>, 
    pub shape_paths: Option<Vec<ShapePath>>,
}

impl FERS {
    // Function to build lookup maps from Vec<Material>, Vec<Section>, and Vec<MemberHinge>
    pub fn build_lookup_maps(
        &self
    ) -> (
        HashMap<u32, &Material>,
        HashMap<u32, &Section>,
        HashMap<u32, &MemberHinge>,
        HashMap<u32, &NodalSupport>
    ) {
        let material_map: HashMap<u32, &Material> = self.materials.iter().map(|m| (m.id, m)).collect();
        let section_map: HashMap<u32, &Section> = self.sections.iter().map(|s| (s.id, s)).collect();
        let memberhinge_map: HashMap<u32, &MemberHinge> = self.memberhinges.iter().flatten().map(|mh| (mh.id, mh)).collect();
        let support_map: HashMap<u32, &NodalSupport> = self.nodal_supports.iter().map(|s| (s.id, s)).collect();
        
        (material_map, section_map, memberhinge_map, support_map)
    }

    pub fn get_member_count(&self) -> usize {
        self.member_sets
            .iter()
            .map(|ms| ms.members.len())
            .sum()
    }

    pub fn assemble_global_stiffness_matrix(&self) -> Result<DMatrix<f64>, String> {
        self.validate_node_ids()?;
        let (material_map, section_map, _memberhinge_map, _support_map) = self.build_lookup_maps();
        let num_dofs: usize = self.member_sets.iter()
            .flat_map(|ms| ms.members.iter())
            .flat_map(|m| vec![m.start_node.id, m.end_node.id])
            .max()
            .unwrap_or(0) as usize * 6; // 6 DOFs per node in 3D
        let mut k_global = DMatrix::<f64>::zeros(num_dofs, num_dofs);

        for member_set in &self.member_sets {
            for member in &member_set.members {
                if let Some(k_local) = member.calculate_stiffness_matrix_3d(&material_map, &section_map) {
                    let t_matrix = member.calculate_transformation_matrix_3d();
                    let k_global_transformed = t_matrix.transpose() * k_local * t_matrix;

                    let si = (member.start_node.id as usize - 1) * 6;
                    let ei = (member.end_node.id   as usize - 1) * 6;
                    for i in 0..6 {
                        for j in 0..6 {
                            k_global[(si + i, si + j)] += k_global_transformed[(i,     j    )];
                            k_global[(si + i, ei + j)] += k_global_transformed[(i,     j + 6)];
                            k_global[(ei + i, si + j)] += k_global_transformed[(i + 6, j    )];
                            k_global[(ei + i, ei + j)] += k_global_transformed[(i + 6, j + 6)];
                        }
                    }
                }
            }
        }

        Ok(k_global)
    }


    pub fn assemble_geometric_stiffness_matrix(
        &self,
        displacement: &DMatrix<f64>,
    ) -> Result<DMatrix<f64>, String> {
        let (material_map, section_map, _hinge_map, _support_map) = self.build_lookup_maps();
        let n = self.compute_num_dofs();
        let mut k_geo = DMatrix::<f64>::zeros(n, n);

        for ms in &self.member_sets {
            for member in &ms.members {
                // 1) axial force in member from current u
                let n_axial = member.calculate_axial_force_3d(
                    displacement, &material_map, &section_map
                );
                // 2) local geometric stiffness
                let k_g_local = member.calculate_geometric_stiffness_matrix_3d(n_axial);
                // 3) transform to global
                let t = member.calculate_transformation_matrix_3d();
                let k_g_global = t.transpose() * k_g_local * t;
                // 4) scatter into k_geo
                let i0 = (member.start_node.id as usize - 1) * 6;
                let j0 = (member.end_node.id   as usize - 1) * 6;
                for i in 0..6 {
                    for j in 0..6 {
                        k_geo[(i0 + i, i0 + j)] += k_g_global[(i,     j    )];
                        k_geo[(i0 + i, j0 + j)] += k_g_global[(i,     j + 6)];
                        k_geo[(j0 + i, i0 + j)] += k_g_global[(i + 6, j    )];
                        k_geo[(j0 + i, j0 + j)] += k_g_global[(i + 6, j + 6)];
                    }
                }
            }
        }

        Ok(k_geo)
    }

    pub fn validate_node_ids(&self) -> Result<(), String> {
        // Collect all node IDs in a HashSet for quick lookup
        let mut node_ids: HashSet<u32> = HashSet::new();

        // Populate node IDs from all members
        for member_set in &self.member_sets {
            for member in &member_set.members {
                node_ids.insert(member.start_node.id);
                node_ids.insert(member.end_node.id);
            }
        }

        // Ensure IDs start at 1 and are consecutive
        let max_id = *node_ids.iter().max().unwrap_or(&0);
        for id in 1..=max_id {
            if !node_ids.contains(&id) {
                return Err(format!("Node ID {} is missing. Node IDs must be consecutive starting from 1.", id));
            }
        }

        Ok(())
    }

    fn compute_num_dofs(&self) -> usize {
        let max_node = self.member_sets.iter()
            .flat_map(|ms| ms.members.iter())
            .flat_map(|m| vec![m.start_node.id, m.end_node.id])
            .max()
            .unwrap_or(0) as usize;
        max_node * 6
    }

   pub fn assemble_load_vector_for_combination(
        &self,
        combination_id: u32,
    ) -> Result<DMatrix<f64>, String> {
        let num_dofs = self.compute_num_dofs();
        let mut f_comb = DMatrix::<f64>::zeros(num_dofs, 1);

        // Find the combination by its load_combination_id field
        let combo = self
            .load_combinations
            .iter()
            .find(|lc| lc.load_combination_id == combination_id)
            .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;

        // Now iterate the HashMap<u32, f64>
        for (&case_id, &factor) in &combo.load_cases_factors {
            let f_case = self.assemble_load_vector_for_case(case_id);
            f_comb += f_case * factor;
        }

        Ok(f_comb)
    }


    pub fn apply_boundary_conditions(&self, k_global: &mut DMatrix<f64>) {
        // Build the support mapping from support id to &NodalSupport.
        // This maps the nodal support definitions provided in FERS.
        let support_map: HashMap<u32, &NodalSupport> = self
            .nodal_supports
            .iter()
            .map(|support| (support.id, support))
            .collect();

        // Create a set to keep track of node IDs that have already had their boundary conditions applied.
        let mut applied_nodes: HashSet<u32> = HashSet::new();

        // Loop over each memberset and each member within
        for member_set in &self.member_sets {
            for member in &member_set.members {
                // Process both the start and end nodes of the member.
                for node in [&member.start_node, &member.end_node] {
                    // Check if we've already applied the BC for this node.
                    if applied_nodes.contains(&node.id) {
                        continue;
                    }

                    // Only apply a BC if the node has a nodal support assigned.
                    if let Some(support_id) = node.nodal_support {
                        // Attempt to retrieve the corresponding nodal support from the support_map.
                        if let Some(support) = support_map.get(&support_id) {
                            self.constrain_dof(k_global, node.id, support);
                            applied_nodes.insert(node.id);
                        }
                    }
                }
            }
        }
    }


    // Helper function to apply constraints based on support
    fn constrain_dof(&self, k_global: &mut DMatrix<f64>, node_id: u32, support: &NodalSupport) {
        let dof_start = (node_id as usize - 1) * 6;

        // Constrain translational DOFs based on displacement conditions
        for (axis, condition) in &support.displacement_conditions {
            let dof = match axis.as_str() {
                "X" => 0,  // X translation
                "Y" => 1,  // Y translation
                "Z" => 2,  // Z translation
                _ => continue,
            };
            match condition.as_str() {
                "Fixed" => self.constrain_single_dof(k_global, dof_start + dof),
                "Free"  => {
                    // DOF is free, so do nothing
                },
                // Optionally handle other conditions (e.g., "Pinned") here
                _ => continue,
            }
        }

        // Constrain rotational DOFs based on rotation conditions
        for (axis, condition) in &support.rotation_conditions {
            let dof = match axis.as_str() {
                "X" => 3,  // X rotation
                "Y" => 4,  // Y rotation
                "Z" => 5,  // Z rotation
                _ => continue,
            };
            match condition.as_str() {
                "Fixed" => self.constrain_single_dof(k_global, dof_start + dof),
                "Free"  => {
                    // Rotation is free, so leave it unmodified.
                },
                _ => continue,
            }
        }
    }

    // Helper function to apply constraints to a single DOF by modifying k_global
    fn constrain_single_dof(&self, k_global: &mut DMatrix<f64>, dof_index: usize) {
        // Zero out the row and column for this constrained DOF
        for j in 0..k_global.ncols() {
            k_global[(dof_index, j)] = 0.0;
        }
        for i in 0..k_global.nrows() {
            k_global[(i, dof_index)] = 0.0;
        }
        k_global[(dof_index, dof_index)] = 1e20;  // Large value to simulate constraint
    }

    pub fn assemble_load_vector_for_case(&self, load_case_id: u32) -> DMatrix<f64> {
        let num_dofs = self.member_sets.iter()
            .flat_map(|ms| ms.members.iter())
            .flat_map(|m| vec![m.start_node.id, m.end_node.id])
            .max()
            .unwrap_or(0) as usize * 6;
        let mut f = DMatrix::<f64>::zeros(num_dofs, 1);
    
        if let Some(load_case) = self.load_cases.iter().find(|lc| lc.id == load_case_id) {
            assemble_nodal_loads(load_case, &mut f);
            assemble_nodal_moments(load_case, &mut f);
            assemble_distributed_loads(load_case, &self.member_sets, &mut f, load_case_id);
        }
        f
    }

    pub fn solve_for_load_case(&mut self, load_case_id: u32) -> Result<Results, String> {
        // a) validate & build stiffness
        self.validate_node_ids()?;
        let original_k = self.assemble_global_stiffness_matrix()?;
        let mut k_global = original_k.clone();

        // b) apply supports
        self.apply_boundary_conditions(&mut k_global);

        // c) build load vector
        let f = self.assemble_load_vector_for_case(load_case_id);

        // d) solve K u = f
        let u = k_global.clone()
            .lu()
            .solve(&f)
            .ok_or_else(|| String::from("Global stiffness matrix is singular or near-singular"))?;

        // e) reaction = K₀·u – f
        let reaction = &original_k * &u - &f;

        let load_case = self
            .load_cases
            .iter()
            .find(|lc| lc.id == load_case_id)
            .ok_or_else(|| format!("LoadCase {} not found.", load_case_id))?;
        let name: String = load_case.name.clone();

        // f) build & store results with the real name
        let results = self.build_and_store_results(
            name,
            ResultType::Loadcase(load_case_id),
            &u,
            &reaction,
        )?;
        Ok(results.clone())
    }

    pub fn solve_for_load_case_second_order(
        &mut self,
        load_case_id: u32,
        max_iterations: usize,
        tolerance: f64,
    ) -> Result<Results, String> {
        self.validate_node_ids()?;
        // assemble linear stiffness & load
        let k_linear = self.assemble_global_stiffness_matrix()?;
        let f = self.assemble_load_vector_for_case(load_case_id);

        let load_case = self
            .load_cases
            .iter()
            .find(|lc| lc.id == load_case_id)
            .ok_or_else(|| format!("LoadCase {} not found.", load_case_id))?;
        let name: String = load_case.name.clone();

        // initial guess
        let mut u = DMatrix::<f64>::zeros(k_linear.nrows(), 1);
        for iter in 0..max_iterations {
            let k_geo = self.assemble_geometric_stiffness_matrix(&u)?;
            let mut k_tangent = &k_linear + &k_geo;
            self.apply_boundary_conditions(&mut k_tangent);

            let r = &k_linear * &u + &k_geo * &u - &f;
            let delta_u = k_tangent
                .clone()
                .lu()
                .solve(&(-&r))
                .ok_or_else(|| "Tangent stiffness singular.".to_string())?;

            u += &delta_u;
            if delta_u.norm() < tolerance {
                break;
            }
            if iter + 1 == max_iterations {
                return Err(format!(
                    "Newton–Raphson failed to converge in {} iterations",
                    max_iterations
                ));
            }
        }

        let reaction = &k_linear * &u - &f;
        // g) build & store results with the real name
        let results = self.build_and_store_results(
            name,
            ResultType::Loadcase(load_case_id),
            &u,
            &reaction,
        )?;
        Ok(results.clone())
    }

    pub fn solve_for_load_combination(
        &mut self,
        combination_id: u32,
    ) -> Result<Results, String> {
        self.validate_node_ids()?;
        let original_k = self.assemble_global_stiffness_matrix()?;
        let mut k_global = original_k.clone();

        self.apply_boundary_conditions(&mut k_global);
        let f_comb = self.assemble_load_vector_for_combination(combination_id)?;

        let u = k_global
            .clone()
            .lu()
            .solve(&f_comb)
            .ok_or_else(|| "Global stiffness matrix singular or near‐singular.".to_string())?;

        let reaction = &original_k * &u - &f_comb;

        // ** lookup the LoadCombination and pull its real name **
        let combo = self
            .load_combinations
            .iter()
            .find(|lc| lc.load_combination_id == combination_id)
            .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;
        let name = combo.name.clone();

        // build & store results with the real name
        let results = self.build_and_store_results(
            name,
            ResultType::Loadcombination(combination_id),
            &u,
            &reaction,
        )?;
        Ok(results.clone())
    }

    pub fn solve_for_load_combination_second_order(
            &mut self,
            combination_id: u32,
            max_iterations: usize,
            tolerance: f64,
        ) -> Result<Results, String> {
            // 1) Validate & build linear stiffness and combined load
            self.validate_node_ids()?;
            let k_linear = self.assemble_global_stiffness_matrix()?;
            let f_comb = self.assemble_load_vector_for_combination(combination_id)?;

            // 2) Initialize displacement vector
            let mut u = DMatrix::<f64>::zeros(k_linear.nrows(), 1);

            // 3) Newton–Raphson loop
            for iter in 0..max_iterations {
                // a) geometric stiffness at current u
                let k_geo = self.assemble_geometric_stiffness_matrix(&u)?;
                // b) form tangent stiffness = K_L + K_G
                let mut k_tangent = &k_linear + &k_geo;
                self.apply_boundary_conditions(&mut k_tangent);

                // c) residual R = (K_L + K_G)·u – F
                let r = &k_linear * &u + &k_geo * &u - &f_comb;

                // d) solve for Δu:  K_tangent · Δu = –R
                let delta_u = k_tangent
                    .clone()
                    .lu()
                    .solve(&(-&r))
                    .ok_or_else(|| "Tangent stiffness singular.".to_string())?;

                // e) update
                u += &delta_u;

                // f) check convergence
                if delta_u.norm() < tolerance {
                    break;
                }
                if iter + 1 == max_iterations {
                    return Err(format!(
                        "Newton–Raphson did not converge in {} iterations.",
                        max_iterations
                    ));
                }
            }

            // 4) Compute reactions
            let reaction = &k_linear * &u - &f_comb;

            // 5) Lookup combo for its name
            let combo = self
                .load_combinations
                .iter()
                .find(|lc| lc.load_combination_id == combination_id)
                .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;

            // 6) Build and store Results
            let results = self.build_and_store_results(
                combo.name.clone(),
                ResultType::Loadcombination(combination_id),
                &u,
                &reaction,
            )?;
            Ok(results.clone())
        }



    pub fn build_and_store_results(
        &mut self,
        name: String,
        result_type: ResultType,
        displacement: &DMatrix<f64>,
        reaction: &DMatrix<f64>,
    ) -> Result<&Results, String> {
        // 1) Compute real member forces
        let member_forces = self.compute_member_forces_from_displacement(displacement);

        // 2) Build min/max maps
        let mut member_minimums = MemberResultMap { data: HashMap::new() };
        let mut member_maximums = MemberResultMap { data: HashMap::new() };

        for mf in &member_forces {
            let id_key = format!("Member {}", mf.member_id);
            let mut mins = HashMap::new();
            let mut maxs = HashMap::new();

            for &(label, start_val, end_val) in &[
                ("fx", mf.start_node_forces.fx, mf.end_node_forces.fx),
                ("fy", mf.start_node_forces.fy, mf.end_node_forces.fy),
                ("fz", mf.start_node_forces.fz, mf.end_node_forces.fz),
                ("mx", mf.start_node_forces.mx, mf.end_node_forces.mx),
                ("my", mf.start_node_forces.my, mf.end_node_forces.my),
                ("mz", mf.start_node_forces.mz, mf.end_node_forces.mz),
            ] {
                mins.insert(label.to_string(), start_val.min(end_val));
                maxs.insert(label.to_string(), start_val.max(end_val));
            }

            member_minimums.data.insert(id_key.clone(), mins);
            member_maximums.data.insert(id_key, maxs);
        }

        // 3) Assemble the Results struct
        let res = Results {
            name: name.clone(),
            result_type: result_type.clone(),
            displacement_nodes: self.extract_displacements(displacement),
            reaction_forces:     self.extract_reaction_forces(reaction),
            member_forces,
            summary: ResultsSummary {
                total_displacements:   self.member_sets.iter().map(|ms| ms.members.len()).sum(),
                total_reaction_forces: self.nodal_supports.len(),
                total_member_forces:   self.member_sets.iter().map(|ms| ms.members.len()).sum(),
            },
            member_minimums: Some(member_minimums),
            member_maximums: Some(member_maximums),
            unity_checks:    None,
        };

        // 4) Insert into bundle
        let bundle = self.results.get_or_insert_with(|| ResultsBundle {
            loadcases:        BTreeMap::new(),
            loadcombinations: BTreeMap::new(),
            unity_checks_overview: None,
        });

        match result_type {
            ResultType::Loadcase(_) => {
                if bundle.loadcases.insert(name.clone(), res).is_some() {
                    return Err(format!("Duplicate load‐case name `{}`", name));
                }
                Ok(bundle.loadcases.get(&name).unwrap())
            }
            ResultType::Loadcombination(_) => {
                if bundle.loadcombinations.insert(name.clone(), res).is_some() {
                    return Err(format!("Duplicate load‐combination name `{}`", name));
                }
                Ok(bundle.loadcombinations.get(&name).unwrap())
            }
        }
    }



    #[allow(dead_code)]
    fn print_matrix(matrix: &DMatrix<f64>, name: &str) {
        if log::log_enabled!(log::Level::Debug) {
            println!("{} ({}x{}):", name, matrix.nrows(), matrix.ncols());
            for i in 0..matrix.nrows() {
                for j in 0..matrix.ncols() {
                    print!("{:10.2} ", matrix[(i, j)]);
                }
                println!();
            }
            println!();
        }
    }

    // fn save_matrix_to_csv(matrix: &DMatrix<f64>, file_path: &str) -> Result<(), Box<dyn Error>> {
    //     let mut wtr = Writer::from_path(file_path)?;
    
    //     for i in 0..matrix.nrows() {
    //         let row: Vec<String> = (0..matrix.ncols())
    //             .map(|j| format!("{:.6}", matrix[(i, j)])) // Format each element to 6 decimal places
    //             .collect();
    //         wtr.write_record(&row)?;
    //     }
    
    //     wtr.flush()?; // Ensure all data is written to the file
    //     log::debug!("Matrix saved to '{}'", file_path);
    
    //     Ok(())
    // }

    fn extract_displacements(&self, u: &DMatrix<f64>) -> BTreeMap<u32, NodeDisplacement> {
        // Collect unique node IDs from all members
        let mut unique_node_ids: HashSet<u32> = HashSet::new();
        for member_set in &self.member_sets {
            for member in &member_set.members {
                unique_node_ids.insert(member.start_node.id);
                unique_node_ids.insert(member.end_node.id);
            }
        }
    
        // Map each unique node ID to its corresponding displacements from u
        unique_node_ids
            .into_iter()
            .map(|node_id| {
                let dof_start = (node_id as usize - 1) * 6;
                (
                    node_id,
                    NodeDisplacement {
                        dx: u[(dof_start, 0)],
                        dy: u[(dof_start + 1, 0)],
                        dz: u[(dof_start + 2, 0)],
                        rx: u[(dof_start + 3, 0)],
                        ry: u[(dof_start + 4, 0)],
                        rz: u[(dof_start + 5, 0)],
                    },
                )
            })
            .collect()
    }

    fn compute_member_forces_from_displacement(
        &self,
        displacement: &DMatrix<f64>,
    ) -> Vec<MemberForce> {
        let (material_map, section_map, _hinge_map, _support_map) = self.build_lookup_maps();
        let mut real_forces = Vec::new();

        for member_set in &self.member_sets {
            for member in &member_set.members {
                // 1) Gather the 12 DOFs for this member
                let start_idx = (member.start_node.id as usize - 1) * 6;
                let end_idx   = (member.end_node.id   as usize - 1) * 6;
                let mut u_member = DVector::<f64>::zeros(12);
                for i in 0..6 {
                    u_member[i]     = displacement[(start_idx + i, 0)];
                    u_member[i + 6] = displacement[(end_idx   + i, 0)];
                }

                // 2) Get local stiffness and transformation
                let k_local  = member
                    .calculate_stiffness_matrix_3d(&material_map, &section_map)
                    .expect("failed to get local stiffness");
                let t_matrix = member.calculate_transformation_matrix_3d();

                // 3) Local forces
                let u_local = &t_matrix * &u_member;
                let f_local = &k_local  * &u_local;

                // 4) Back to global
                let f_global = t_matrix.transpose() * f_local;

                // 5) Split into NodeForces
                let start_forces = NodeForces {
                    fx: f_global[0],
                    fy: f_global[1],
                    fz: f_global[2],
                    mx: f_global[3],
                    my: f_global[4],
                    mz: f_global[5],
                };
                let end_forces = NodeForces {
                    fx: f_global[6],
                    fy: f_global[7],
                    fz: f_global[8],
                    mx: f_global[9],
                    my: f_global[10],
                    mz: f_global[11],
                };

                real_forces.push(MemberForce {
                    member_id: member.id,
                    start_node_forces: start_forces,
                    end_node_forces:   end_forces,
                });
            }
        }

        real_forces
    }

    fn extract_reaction_forces(&self, r: &DMatrix<f64>) -> Vec<ReactionForce> {
        self.nodal_supports
            .iter()
            .enumerate()
            .map(|(support_id, support)| {
                let dof_start = (support_id) * 6;
                ReactionForce {
                    support_id: support.id,
                    fx: r[(dof_start, 0)],
                    fy: r[(dof_start + 1, 0)],
                    fz: r[(dof_start + 2, 0)],
                    mx: r[(dof_start + 3, 0)],
                    my: r[(dof_start + 4, 0)],
                    mz: r[(dof_start + 5, 0)],
                }
            })
            .collect()
    }


    pub fn save_results_to_json(fers_data: &FERS, file_path: &str) -> Result<(), std::io::Error> {
        let json = serde_json::to_string_pretty(fers_data)?; 
        std::fs::write(file_path, json) 
    }


}