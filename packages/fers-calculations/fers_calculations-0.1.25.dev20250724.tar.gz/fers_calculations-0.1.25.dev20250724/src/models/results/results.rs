use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap};
use utoipa::ToSchema;
use crate::models::results::forces::{ReactionForce, MemberForce};
use crate::models::results::resultssummary::ResultsSummary;
use crate::models::results::memberresultmap::MemberResultMap;
use crate::models::unitychecks::unitycheck::UnityCheck;

use super::displacement::NodeDisplacement;

#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub enum ResultType {
    Loadcase(u32),
    Loadcombination(u32),
}


#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct Results {
    pub name: String,
    pub result_type: ResultType,
    pub displacement_nodes: BTreeMap<u32, NodeDisplacement>,
    pub reaction_forces: Vec<ReactionForce>,
    pub member_forces: Vec<MemberForce>,
    pub summary: ResultsSummary,
    pub member_minimums: Option<MemberResultMap>,
    pub member_maximums: Option<MemberResultMap>,
    pub unity_checks: Option<BTreeMap<String, UnityCheck>>,
}


