const fs = require("fs");

const BASE = "https://api.gateway.nawa.ncnp.gov.sa/graphql";
main();

async function getContactDetails(id = 1) {
  const response = await fetch(BASE, {
    headers: {
      "content-type": "application/json",
    },
    body: `
    {\"query\":\"query FindEntityContacts(\\n  $entityId: Int!,\\n) {\\n  findEntityContactByEntityId(entityId: $entityId) {\\n    createdAt\\n    email\\n    entityId\\n    facebookAccount\\n    id\\n    instagramAccount\\n    linkedinAccount\\n    phoneNumber\\n    snapchatAccount\\n    telephoneNumber\\n    twitterAccount\\n    unifiedNumber\\n    updatedAt\\n    website\\n  }\\n}\",\"variables\":{\"entityId\":${id}}}
    `,
    method: "POST",
  });

  const data = await response.json();

  if (data.error) {
    return {}
  }

  return data.data.findEntityContactByEntityId;
}

async function getMembersDetails(id = 1) {
  const response = await fetch(BASE, {
    headers: {
      "content-type": "application/json",
    },
    body: `
    {\"query\":\"query FindEntityAdditionalInfo($entityId: Int!) {\\n  membershipConditions(entityId: $entityId) {\\n    membershipConditions {\\n      type\\n    }\\n  }\\n  publicMemberships(unitId: $entityId) {\\n    memberships {\\n      id\\n      foundingMember\\n      familyRelation {\\n        enTitle\\n        arTitle\\n      }\\n      specialized\\n      member {\\n        firstName\\n        fatherName\\n        grandfatherName\\n        lastName\\n        nationalId\\n        birthDateHijri\\n        absherPhone\\n        occupation\\n        previousExperience\\n        educationalLevel\\n        employmentPlace\\n        educationSpecialization\\n      }\\n      position {\\n        arTitle\\n        enTitle\\n      }\\n      role\\n    }\\n  }\\n}\",\"variables\":{\"entityId\":${id}}}
    `,
    method: "POST",
  });

  const data = await response.json();

  return data.data.publicMemberships.memberships;
}

async function getDetails(id = 1) {
  const response = await fetch("https://api.gateway.nawa.ncnp.gov.sa/graphql", {
    headers: {
      "content-type": "application/json",
    },
    body: `
    {\"query\":\"query FindEntityByIDForProfile($id: Int!) {\\n  entityProfile(id: $id) {\\n    entityProfile {\\n  logo {\\n    origin {\\n      attachedAt\\n      url: path\\n      uid\\n    }\\n    x100 {\\n      attachedAt\\n      url: path\\n      uid\\n    }\\n    x200 {\\n      attachedAt\\n      url: path\\n      uid\\n    }\\n    x300 {\\n      attachedAt\\n      url: path\\n      uid\\n    }\\n    x500 {\\n      attachedAt\\n      url: path\\n      uid\\n    }\\n  }\\n}\\n    \\nareasOfActivity {\\n  cities {\\n    arTitle\\n    enTitle\\n    regionCode\\n    uid\\n  }\\n  cityUids\\n  entityId\\n  region {\\n    arTitle\\n    cities {\\n      arTitle\\n      enTitle\\n      regionCode\\n      uid\\n    }\\n    code\\n    enTitle\\n  }\\n  regionCode\\n  type\\n}\\n    entityNationalAddress {\\n      additionalNumber\\n      buildingNumber\\n      postCode\\n      streetName\\n    }\\n    licenseNumber700\\n    foundFor\\n    memberRole\\n    unifiedNumber700\\n    id\\n    type\\n    entityUid\\n    nameArabic\\n    nameEnglish\\n    acceptedAt\\n    registrationDateHijri\\n    typeOfBenefits\\n    entityLicenseNumber\\n    membershipType\\n    isDocsExposed\\n    city {\\n      arTitle\\n      enTitle\\n    }\\n    region {\\n      arTitle\\n      enTitle\\n    }\\n    secondSubClassificationId\\n    classificationDetails {\\n      mainClassificationArTitle\\n      firstSubClassificationArTitle\\n      secondSubClassificationArTitle\\n      departmentArTitle\\n    }\\n    activities {\\n      arTitle\\n    }\\n    goals {\\n      ... on CommonGoal {\\n        arTitle\\n      }\\n      ... on FamilyTrustGoal {\\n        arTitle\\n        enTitle\\n      }\\n    }\\n    isNama\\n    entityLicenses {\\n  uid\\n}\\n    bankCertificates {\\n  uid\\n}\\n    eligibilityStudyFiles {\\n  uid\\n}\\n    entityPolicies {\\n  uid\\n}\\n    establishmentDecisions {\\n  uid\\n}\\n    migrationDelegateLetters {\\n  uid\\n}\\n    supportingDocuments {\\n  uid\\n}\\n  }\\n}\",\"variables\":{\"id\":${id}}}
    `,
    method: "POST",
  });

  const data = await response.json();

  return data.data.entityProfile;
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function main() {
  for (let idx = 1; idx <= 489; idx++) {
    {
      await sleep(100);
      const response = await fetch(BASE, {
        headers: {
          "content-type": "application/json",
        },
        body: `
        {\"query\":\"query FetchFilteredEntities(\\n  $page: Int!,\\n  $size: Int!,\\n  $name: String,\\n  $mainClassificationId: Int,\\n  $firstSubClassificationId: Int,\\n  $secondSubClassificationId: Int,\\n  $hijriDateFrom: String,\\n  $hijriDateTo: String,\\n  $goalId: Int,\\n  $activityId: Int,\\n  $type: EntityType,\\n  $excludedType: [EntityType!],\\n  $regionCode: String\\n  $cityUid: [String!]\\n  $entityUid: String\\n  $unifiedNumber700: String\\n){\\n  publicListEntities(\\n    page: $page\\n    size: $size\\n    name: $name\\n    mainClassificationId: $mainClassificationId\\n    firstSubClassificationId: $firstSubClassificationId\\n    secondSubClassificationId: $secondSubClassificationId\\n    hijriDateFrom: $hijriDateFrom\\n    hijriDateTo: $hijriDateTo\\n    goalId: $goalId\\n    activityId: $activityId\\n    type: $type\\n    excludedType: $excludedType\\n    regionCode: $regionCode\\n    cityUid: $cityUid\\n    entityUid: $entityUid\\n    unifiedNumber700: $unifiedNumber700\\n  ) {\\n    entities {\\n      entityLicenseNumber\\n      unifiedNumber700\\n      entityProfile {\\n        logo {\\n          origin {\\n            url: path\\n            uid\\n          }\\n          x100 {\\n            url: path\\n            uid\\n          }\\n          x200 {\\n            url: path\\n            uid\\n          }\\n          x300 {\\n            url: path\\n            uid\\n          }\\n          x500 {\\n            url: path\\n            uid\\n          }\\n        }\\n      }\\n      activities{\\n        arTitle\\n      }\\n      owner {\\n        id\\n      }\\n      createdAt\\n      acceptedAt\\n      foundFor\\n      classificationDetails{\\n        mainClassificationArTitle\\n        firstSubClassificationArTitle\\n        secondSubClassificationArTitle\\n        departmentArTitle\\n      }\\n\\n      goals {\\n        ... on CommonGoal {\\n          arTitle\\n          id\\n        }\\n        ... on FamilyTrustGoal {\\n          arTitle\\n          enTitle\\n          id\\n        }\\n      }\\n      id\\n      nameArabic\\n      nameEnglish\\n      numberOfBoardMembers\\n      secondSubClassificationId\\n      type\\n      updatedAt\\n      updatedAtHijri: registrationDateHijri\\n    }\\n    meta{\\n      page\\n      pageCount\\n      recordsCount\\n      size\\n    }\\n  }\\n}\",\"variables\":{\"page\":${idx},\"size\":10,\"excludedType\":[\"cooperativeAssociation\"]}}
        `,
        method: "POST",
      });

      const data = await response.json();

      data.data.publicListEntities.entities.forEach(async (el) => {
        let id = el.id;

        let details = await getDetails(id);
        let contactDetails = await getContactDetails(id);
        // let membersDetails = await getMembersDetails(id);

        let data = { ...details , ...contactDetails };

        fs.appendFile("data.jsonl", JSON.stringify(data) + "\n", (e) => {
          if (e) {
            console.log(e);
          }
          console.log(idx)
        });
      });
    }
  }
}
